import sqlite3
from typing import Generator, Optional
import os
from importlib.resources import files, as_file
import logging
import random
from datetime import datetime
from dataclasses import dataclass, field

__version__ = "0.0.6"

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.debug("Dependency 'openai' is not installed. OpenAI functionality will be disabled.")

class QuoteNotFoundError(Exception):
    """Raised when no quote is found in the database for the given criteria."""

class InterpretationNotFoundError(Exception):
    """Raised when no interpretation is found in the database for a given quote."""

@dataclass
class Quote:
    """
    Represents a single quote with its text, author, and optional interpretation.
    """
    text: str
    author: str
    interpretation: Optional[str] = field(default=None)

class Quotes:
    """
    A database manager for quotes, with functionality for fetching and filtering quotes
    and generating interpretations.
    """
    def __init__(self):
        # Dynamically locate the database file relative to the package
        package_name = __package__  # Get the current module's package name
        if not package_name:
            raise ValueError("Cannot determine the package name for locating resources.")

        # Use importlib.resources to locate the database file
        with as_file(files(package_name) / "data" / "quotes.db") as default_db_path:
            if not os.path.isfile(default_db_path):
                raise FileNotFoundError(
                    f"Default database file 'quotes.db' does not exist in '{package_name}/data/'. "
                    "Ensure the file is present in the expected location."
                )
            self.db_path = default_db_path
            self.connection = sqlite3.connect(self.db_path)

        # Use environment variable for OpenAI API key
        if OPENAI_AVAILABLE and os.getenv("OPENAI_API_KEY"):
            self.openai_enabled = True
        else:
            self.openai_enabled = False

    def __del__(self):
        self.connection.close()

    def get_authors(self) -> list[str]:
            """
            Returns a list of all distinct authors in the database.
            """
            with self.connection as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT DISTINCT author FROM quotes ORDER BY author ASC")
                authors = [row[0] for row in cursor.fetchall()]
                return authors

    def get_quote(
        self,
        quote_id: Optional[str] = None,
        author: Optional[str] = None,
        interpretation: Optional[str] = None
    ) -> Quote:
        """
        Fetches and returns a single quote as a Quote object.

        Parameters:
        - quote_id (Optional[str]): If provided, fetches the specific quote with this ID.
                                    Overrides the 'author' parameter if both are provided.
        - author (Optional[str]): If provided, fetches a random quote by this author.
                                  Ignored if 'quote_id' is specified.
        - interpretation (Optional[str]): Specifies how to handle interpretations for the quote. Options are:
            - 'gpt': Generate a new interpretation using GPT.
            - 'db': Fetch a random interpretation from the database.
            - 'gpt+fallback': Attempt to generate an interpretation using GPT. If GPT fails, fallback to a random database interpretation.
            - None: No interpretation is included.

        Returns:
        - Quote: A Quote object containing the text, author, and optionally an interpretation.

        Raises:
        - ValueError: If the 'interpretation' argument is invalid.
        - RuntimeError: If 'gpt' or 'gpt+fallback' is specified but OpenAI functionality is not enabled.
        - QuoteNotFoundError: If no quote is found based on the provided 'quote_id' or 'author'.
        - InterpretationNotFoundError: If no interpretations are found for the quote when 'db' or 'gpt+fallback' is used.
        """
        if interpretation not in {None, "gpt", "db", "gpt+fallback"}:
            raise ValueError("Interpretation must be 'gpt', 'db', 'gpt+fallback' or None.")

        if interpretation in {"gpt", "gpt+fallback"} and not self.openai_enabled:
            raise RuntimeError("OpenAI functionality is not enabled. Install the 'openai' package and provide an API key.")

        with self.connection as conn:
            cursor = conn.cursor()

            # Check if both quote_id and author are provided
            if quote_id and author:
                logger.info("Author argument is ignored because a quote ID is provided.")

            # If quote_id is provided, fetch the specific quote
            if quote_id:
                cursor.execute("""
                    SELECT * FROM quotes
                    WHERE id = ?
                """, (quote_id,))
            elif author:  # If author is provided, fetch a random quote by the author
                cursor.execute("""
                    SELECT * FROM quotes
                    WHERE author = ?
                    ORDER BY RANDOM()
                    LIMIT 1
                """, (author,))
            else:  # Fetch a completely random quote
                cursor.execute("""
                    SELECT * FROM quotes
                    ORDER BY RANDOM()
                    LIMIT 1
                """)

            row = cursor.fetchone()
            if not row:
                if quote_id:
                    raise QuoteNotFoundError(f"No quote found with ID '{quote_id}'.")
                elif author:
                    raise QuoteNotFoundError(f"No quotes found for author '{author}'.")
                else:
                    raise QuoteNotFoundError("No quotes found.")

            # Create the Quote object
            quote = Quote(text=row[1], author=row[2])
            fallback = False
            # Handle interpretation
            if interpretation == "gpt":
                quote.interpretation = self._generate_interpretation(quote.text, quote.author)
            elif interpretation == "gpt+fallback":
                try:
                    quote.interpretation = self._generate_interpretation(quote.text, quote.author)
                except Exception as e:
                    logger.debug("Error generating interpretation via GPT. Falling back to database.")
                    fallback = True
            elif interpretation == "db" or fallback:
                cursor.execute("""
                    SELECT interpretation FROM interpretations
                    WHERE quote_id = ?
                    ORDER BY RANDOM()
                    LIMIT 1
                """, (row[0],))
                interpretation_row = cursor.fetchone()
                if not interpretation_row:
                    raise InterpretationNotFoundError(f"No interpretations found for quote ID {row[0]}.")
                quote.interpretation = interpretation_row[0]

            return quote


    def get_quotes(
        self,
        author: Optional[str] = None,
        interpretation: Optional[str] = None,
        limit: Optional[int] = None,
        random: bool = True,
    ) -> Generator[Quote, None, None]:
        """
        Returns a generator that iterates over quotes from the database.

        Parameters:
        - author (Optional[str]): Filters quotes by the specified author's name. If None, all authors are included.
        - interpretation (Optional[str]): Specifies how interpretations for the quotes are handled. Options are:
            - 'gpt': Generate a new interpretation using GPT.
            - 'db': Fetch a random interpretation from the database.
            - 'gpt+fallback': Attempt to generate an interpretation using GPT. If GPT fails, fallback to a random database interpretation.
            - None: No interpretation is included.
        - limit (Optional[int]): The maximum number of quotes to fetch. If None, fetches all matching quotes.
        - random (bool): If True, quotes are returned in a random order. Defaults to True.

        Yields:
        - Quote: A Quote object containing the text, author, and optionally an interpretation.

        Raises:
        - ValueError: If the interpretation argument is invalid.
        - RuntimeError: If 'gpt' or 'gpt+fallback' is used but OpenAI functionality is not enabled.
        - InterpretationNotFoundError: If an interpretation is requested but none exists for a quote.
        """

        if interpretation not in {None, "gpt", "db", "gpt+fallback"}:
            raise ValueError("Interpretation must be 'gpt', 'db', 'gpt+fallback' or None.")

        if interpretation in {"gpt", "gpt+fallback"} and not self.openai_enabled:
            raise RuntimeError("OpenAI functionality is not enabled. Install the 'openai' package and provide an API key.")

        with self.connection as conn:
            main_cursor = conn.cursor()
            interpretation_cursor = conn.cursor()  # Separate cursor for interpretations

            # Construct the query
            query = "SELECT * FROM quotes"
            params = []
            if author:
                query += " WHERE author = ?"
                params.append(author)
            if random:
                query += " ORDER BY RANDOM()"  # Add random order if requested
            if limit is not None:
                query += f" LIMIT {limit}"  # Apply the limit directly in the query

            # Execute the query
            main_cursor.execute(query, params)

            for row in main_cursor:
                # Create a Quote object
                quote = Quote(text=row[1], author=row[2])
                fallback = False
                # Fetch interpretation if required
                if interpretation == "gpt":
                    quote.interpretation = self._generate_interpretation(quote.text, quote.author)
                elif interpretation == "gpt+fallback":
                    try:
                        quote.interpretation = self._generate_interpretation(quote.text, quote.author)
                    except Exception as e:
                        logger.debug("Error generating interpretation via GPT. Falling back to database.")
                        fallback = True
                elif interpretation == "db" or fallback:
                    interpretation_cursor.execute(
                        """
                        SELECT interpretation FROM interpretations
                        WHERE quote_id = ?
                        ORDER BY RANDOM()
                        LIMIT 1
                        """,
                        (row[0],),
                    )
                    interpretation_row = interpretation_cursor.fetchone()
                    if not interpretation_row:
                        raise InterpretationNotFoundError(f"No interpretations found for quote ID {row[0]}.")
                    quote.interpretation = interpretation_row[0]

                yield quote

    def _generate_interpretation(self, quote_text: str, author: str) -> str:
        """
        Generates a new interpretation for a quote using OpenAI.
        """
        if not self.openai_enabled:
            raise RuntimeError("OpenAI functionality is not enabled.")


        response = openai.Client().chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": """
                I will provide a Stoic quote. Write a calm, thoughtful explanation of its underlying meaning, suitable for someone new to Stoic philosophy.
                Present your response as a single cohesive paragraph, integrating contemporary scenarios to illustrate the idea in everyday life.
                Begin directly with your interpretation—without using phrases like “this quote means...” or “the quote is saying...”
                —and let the wording of the quote guide your explanation naturally.
                Maintain an accessible, relatable tone that connects the ancient wisdom to modern circumstances.
                """},
                {"role": "user", "content": f"{quote_text} - {author}"},
            ],
            temperature=1,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
            max_tokens=500,
        )
        return response.choices[0].message.content.strip()

    def get_daily_quote(self, interpretation: Optional[str] = "db+fixed") -> Quote:
        """
        Fetches a consistent quote for the current day of the year based on unique random IDs.

        This method uses a deterministic random sampling mechanism to select a quote
        corresponding to the current day of the year. It optionally includes an interpretation
        based on the specified mode.

        Parameters:
        - interpretation (Optional[str]): Specifies how interpretations for the quote are handled. Options are:
            - 'gpt': Generate a new interpretation using GPT.
            - 'db': Fetch a random interpretation from the database.
            - 'db+fixed': Fetch a deterministic interpretation using the current day of the year.
            - 'gpt+fallback': Attempt to generate an interpretation using GPT. If GPT fails, fallback to a random database interpretation.
            - None: No interpretation is included.

        Returns:
        - Quote: A Quote object containing the text, author, and optionally an interpretation.

        Raises:
        - ValueError: If the 'interpretation' argument is invalid, the database is empty, or no quote is found for the selected ID.
        - RuntimeError: If 'gpt' or 'gpt+fallback' is specified but OpenAI functionality is not enabled.
        - InterpretationNotFoundError: If no interpretations are found for the quote when 'db', 'db+fixed', or 'gpt+fallback' is used.

        Notes:
        - This method ensures the same quote is selected for the same day of the year and year, unless the database content changes.
        - 'db+fixed' uses a deterministic approach to select an interpretation based on the current day.
        - 'db' introduces randomness when fetching an interpretation from the database.
        """
        today = datetime.now()
        current_year = today.year
        day_of_year = today.timetuple().tm_yday  # Day of the year (1-366)

        # Validate the interpretation argument
        if interpretation not in {None, "gpt", "db", "db+fixed", "gpt+fallback"}:
            raise ValueError("Interpretation must be 'gpt', 'db', 'db+fixed', 'gpt+fallback', or None.")

        if interpretation in {"gpt", "gpt+fallback"} and not self.openai_enabled:
            raise RuntimeError("OpenAI functionality is not enabled. Install the 'openai' package and provide an API key.")

        # Get the maximum ID from the database
        with self.connection as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT MAX(id) FROM quotes")
            max_id = cursor.fetchone()[0]

            if not max_id:
                raise ValueError("The quotes database is empty.")

        # Generate a random sample of unique IDs
        random.seed(current_year)
        sampled_ids = random.sample(range(1, max_id + 1), min(366, max_id))

        # Select the ID for the current day
        selected_id = sampled_ids[day_of_year - 1]  # Adjust for 0-based indexing

        # Fetch the quote corresponding to the selected ID
        with self.connection as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM quotes WHERE id = ?", (selected_id,))
            row = cursor.fetchone()

            if not row:
                raise ValueError(f"No quote found with ID {selected_id}.")

        # Create the Quote object
        quote = Quote(text=row[1], author=row[2])

        # Handle interpretation
        if interpretation == "gpt":
            quote.interpretation = self._generate_interpretation(quote.text, quote.author)
        elif interpretation == "gpt+fallback":
            try:
                quote.interpretation = self._generate_interpretation(quote.text, quote.author)
            except Exception as e:
                logger.debug("Error generating interpretation via GPT. Falling back to database.")
                interpretation = "db"  # Fall back to DB handling

        if interpretation == "db":
            # Random database-based interpretation
            with self.connection as conn:
                cursor.execute(
                    """
                    SELECT interpretation FROM interpretations
                    WHERE quote_id = ?
                    ORDER BY RANDOM()
                    LIMIT 1
                    """,
                    (row[0],),
                )
                interpretation_row = cursor.fetchone()
                if not interpretation_row:
                    raise InterpretationNotFoundError(f"No interpretations found for quote ID {row[0]}.")
                quote.interpretation = interpretation_row[0]
        elif interpretation == "db+fixed":
            # Deterministic database-based interpretation
            with self.connection as conn:
                cursor.execute(
                    """
                    SELECT interpretation FROM interpretations
                    WHERE quote_id = ?
                    """,
                    (row[0],),
                )
                interpretation_rows = cursor.fetchall()
                if not interpretation_rows:
                    raise InterpretationNotFoundError(f"No interpretations found for quote ID {row[0]}.")

                # Use deterministic randomness for selection
                random.seed(current_year + day_of_year)  # Ensure reproducibility for the current day
                selected_interpretation = random.sample([row[0] for row in interpretation_rows], 1)[0]
                quote.interpretation = selected_interpretation

        return quote

quotes = Quotes()

