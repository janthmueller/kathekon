import argparse
import re
from kathekon import Quotes
from pathlib import Path
from rich.console import Console
from rich.text import Text
from rich.panel import Panel
from rich.align import Align

quotes = Quotes()
console = Console()

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="CLI for Stoic quotes.")
    subparsers = parser.add_subparsers(dest="subcommand")

    # Default behavior: behaves like 'random'
    parser.add_argument("--id", type=int, help="Fetch a quote by its unique ID.")
    parser.add_argument("--author", type=str, default=None, help="Fetch a random quote by the specified author.")
    parser.add_argument("--interpretation", choices=["gpt", "db", "gpt+fallback"], default="db", help="Method to fetch or generate interpretation.")

    # Subcommand: daily
    daily_parser = subparsers.add_parser("daily", help="Display today's Stoic quote.")
    daily_parser.add_argument("--interpretation", choices=["gpt", "db", "db+fixed", "gpt+fallback"], default="db+fixed", help="Method to fetch or generate interpretation.")

    # Subcommand: readme
    readme_parser = subparsers.add_parser("readme", help="Update README.md or provided file with a Stoic quote.")
    readme_subparsers = readme_parser.add_subparsers(dest="quote_type", required=True)

    # Sub-subcommand: readme random
    readme_random_parser = readme_subparsers.add_parser("random", help="Update with a random quote.")
    readme_random_parser.add_argument("--file", type=str, default="README.md", help="Path to the file to update.")
    readme_random_parser.add_argument("--id", type=int, help="Fetch a quote by its unique ID.")
    readme_random_parser.add_argument("--author", type=str, default=None, help="Fetch a random quote by the specified author.")
    readme_random_parser.add_argument("--interpretation", choices=["gpt", "db", "gpt+fallback"], default="db", help="Method to fetch or generate interpretation.")

    # Sub-subcommand: readme daily
    readme_daily_parser = readme_subparsers.add_parser("daily", help="Update with today's quote.")
    readme_daily_parser.add_argument("--file", type=str, default="README.md", help="Path to the file to update.")
    readme_daily_parser.add_argument("--interpretation", choices=["gpt", "db", "db+fixed", "gpt+fallback"], default="db+fixed", help="Method to fetch or generate interpretation.")

    args = parser.parse_args()

    if args.subcommand == "daily":
        handle_daily_stoic(args.interpretation)
    elif args.subcommand == "readme":
        if args.quote_type == "random":
            handle_update_readme_random(args.file, args.id, args.author, args.interpretation)
        elif args.quote_type == "daily":
            handle_update_readme_daily(args.file, args.interpretation)
    else:
        handle_random_stoic(args.id, args.author, args.interpretation)

def handle_random_stoic(quote_id, author, interpretation):
    """Handles the default/random behavior."""
    try:
        quote = quotes.get_quote(quote_id=quote_id, author=author, interpretation=interpretation)
        output = format_quote(quote.text, quote.author, quote.interpretation)
        console.print(output)
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")

def handle_daily_stoic(interpretation):
    """Handles the 'daily' subcommand."""
    try:
        quote = quotes.get_daily_quote(interpretation=interpretation)
        output = format_quote(quote.text, quote.author, quote.interpretation)
        console.print(output)
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")

def handle_update_readme_random(file_path, quote_id, author, interpretation):
    """Handles updating the README with a random quote."""
    try:
        quote = quotes.get_quote(quote_id=quote_id, author=author, interpretation=interpretation)
        update_readme(file_path, quote)
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")

def handle_update_readme_daily(file_path, interpretation):
    """Handles updating the README with today's quote."""
    try:
        quote = quotes.get_daily_quote(interpretation=interpretation)
        update_readme(file_path, quote)
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")

def update_readme(file_path, quote):
    """Helper to update README file with a given quote."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"The file {file_path} does not exist.")
    content = path.read_text()
    replacements = {
        "quote-text": quote.text,
        "quote-author": quote.author,
        "quote-interpretation": quote.interpretation or "",
    }
    for section, replacement in replacements.items():
        content = replace_section(content, section, replacement)
    path.write_text(content)
    console.print(f"Updated {file_path} successfully.")

def format_quote(text, author, interpretation):
    """Formats the quote, author, and interpretation for terminal output using rich."""
    formatted_text = Text(f'“{text}”\n', style="italic")
    formatted_author = Text(f'— {author}\n', style="bold")
    components = [formatted_text, formatted_author]
    if interpretation:
        components.append(Text(f'\n{interpretation}'))
    quote_content = Panel(
        Align.center(Text.assemble(*components), vertical="middle"),
        expand=False,
        title="Stoic Quote",
        border_style="bright_white"
    )
    return quote_content

def replace_section(content, section_name, replacement):
    """Replaces a section in the content with the given replacement."""
    pattern = rf"(<!--START_SECTION:{section_name}-->)(.*?)(<!--END_SECTION:{section_name}-->)"
    replacement_content = rf"\1\n{replacement}\n\3"
    return re.sub(pattern, replacement_content, content, flags=re.DOTALL)

if __name__ == "__main__":
    main()
