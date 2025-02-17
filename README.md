# kathekon

[![PyPI Latest Release](https://img.shields.io/pypi/v/kathekon.svg)](https://pypi.org/project/kathekon/)
[![Pepy Total Downloads](https://img.shields.io/pepy/dt/kathekon)](https://pepy.tech/project/kathekon)
[![GitHub License](https://img.shields.io/github/license/janthmueller/kathekon)](https://github.com/janthmueller/kathekon/blob/main/LICENSE)

**kathekon** is a Python library and CLI tool for exploring Stoic philosophy through curated quotes. It allows you to fetch random or daily quotes, insert quotes into files like `README.md`, and generate thoughtful interpretations using OpenAI.

---

## Features

- **Fetch Quotes**:
  - Retrieve random Stoic quotes or specific quotes by author or ID.
  - Generate consistent daily quotes based on the day of the year.
  - Fetch multiple quotes at once for broader inspiration.

- **CLI Tool**:
  - Display quotes in the terminal with elegant formatting.
  - Update files (e.g., `README.md`) with quotes and their interpretations.
  - Customize quote fetching using multiple filtering options.

- **OpenAI Integration** *(Optional)*:
  - Generate thoughtful interpretations of quotes using OpenAI's GPT models.

- **Library Integration**:
  - Use `Quotes` from the library to integrate Stoic philosophy into your projects.

---

## Installation

Install `kathekon` using pip:

```bash
pip install kathekon
```

To include OpenAI features, install with the `[openai]` or `[all]` extras:

```bash
pip install kathekon[openai]
pip install kathekon[all]
```

---

## Usage

### CLI Commands

After installation, you can use the CLI commands `kathekon` or `stoic-quote`.

#### Display a Random Quote

```bash
kathekon --author "Marcus Aurelius"
```

#### Display Today’s Quote

```bash
kathekon daily
```

#### Insert a Quote into `README.md`

Ensure your `README.md` includes markers like this:

```markdown
<!--START_SECTION:quote-text-->
<!--END_SECTION:quote-text-->

<!--START_SECTION:quote-author-->
<!--END_SECTION:quote-author-->

<!--START_SECTION:quote-interpretation-->
<!--END_SECTION:quote-interpretation-->
```

Then, insert a random or daily quote:

```bash
# Insert a random quote by Marcus Aurelius
kathekon readme random --file README.md --author "Marcus Aurelius"

# Insert today’s Stoic quote
kathekon readme daily --file README.md
```

### Available CLI Arguments

#### General Options (for default/random quote behavior)
These options can be used when **running the CLI without a subcommand**, which will display a **random quote**.

| Argument                      | Short | Description                                                                                              | Default |
|-------------------------------|-------|----------------------------------------------------------------------------------------------------------|---------|
| `--id ID`                     | `-i`  | Fetch a quote by its unique ID. If omitted, a **random quote** is used.                                  | None    |
| `--author "Author Name"`       | `-a`  | Fetch a random quote by the specified author. If omitted, **a random author is chosen**.                 | None    |
| `--method METHOD`              | `-m`  | Choose method to fetch or generate interpretation: `gpt`, `db`, `gpt+fallback`                          | `db`    |
| `--list-authors`               | `-l`  | List all available authors and exit.                                                                     | -       |
| `--version`                    | `-v`  | Show version and exit.                                                                                    | -       |

---

#### Method Choices Explained
| Method         | Description                                                                                          |
|----------------|------------------------------------------------------------------------------------------------------|
| `gpt`          | Generate a quote interpretation using OpenAI's GPT models. Requires an API key.                     |
| `db`           | Fetch a (random) existing interpretation from the database.                                          |
| `gpt+fallback` | Try generating an interpretation using GPT. If unavailable, fall back to a database interpretation. |
| `db+fixed`     | Use a fixed interpretation from the database, ensuring consistency for `daily` quotes.                 |

---

#### `daily` Command
Displays **today’s Stoic quote**.

| Argument                     | Short | Description                                                                                              | Default    |
|------------------------------|-------|----------------------------------------------------------------------------------------------------------|------------|
| `--method METHOD`             | `-m`  | Choose method to fetch or generate interpretation: `gpt`, `db`, `db+fixed`, `gpt+fallback`              | `db+fixed` |

---

#### `readme random` Command
Updates the specified file with a **random quote**.

| Argument                     | Short | Description                                                                                              | Default    |
|------------------------------|-------|----------------------------------------------------------------------------------------------------------|------------|
| `--file FILE`                 | `-f`  | Path to the file to update                                                                                | `README.md` |
| `--id ID`                     | `-i`  | Fetch a quote by its unique ID. If omitted, a **random quote** is used.                                  | None       |
| `--author "Author Name"`       | `-a`  | Fetch a random quote by the specified author. If omitted, **a random author is chosen**.                 | None       |
| `--method METHOD`             | `-m`  | Choose method to fetch or generate interpretation: `gpt`, `db`, `gpt+fallback`                          | `db`       |

---

#### `readme daily` Command
Updates the specified file with **today’s Stoic quote**.

| Argument                     | Short | Description                                                                                              | Default    |
|------------------------------|-------|----------------------------------------------------------------------------------------------------------|------------|
| `--file FILE`                 | `-f`  | Path to the file to update                                                                                | `README.md` |
| `--method METHOD`             | `-m`  | Choose method to fetch or generate interpretation: `gpt`, `db`, `db+fixed`, `gpt+fallback`              | `db+fixed` |

---

## Library Usage

### Fetch a Random Quote
```python
from kathekon import Quotes

quotes = Quotes()
quote = quotes.get_quote(author="Epictetus")
print(f"{quote.text} — {quote.author}")
```

### Generate Today’s Quote
```python
daily_quote = quotes.get_daily_quote(method="gpt+fallback")
print(f"{daily_quote.text} — {daily_quote.author}")
print(f"Interpretation: {daily_quote.interpretation}")
```

### Fetch Multiple Quotes
You can fetch multiple quotes at once with optional filters like `author`, `limit`, or `interpretation`.

```python
from kathekon import Quotes

quotes = Quotes()

# Fetch up to 5 random quotes
for quote in quotes.get_quotes(limit=5):
    print(f"{quote.text} — {quote.author}")

# Fetch 3 quotes by Seneca with interpretations from the database
for quote in quotes.get_quotes(author="Seneca", limit=3, method="db"):
    print(f"{quote.text} — {quote.author}")
    print(f"Interpretation: {quote.interpretation}")
```

---

## OpenAI Integration

To enable OpenAI-powered interpretations, set your API key in the `OPENAI_API_KEY` environment variable:

```bash
export OPENAI_API_KEY="your-api-key"
```

Then, use the CLI or library to fetch quotes with AI-generated interpretations.

---

## Contributing

Contributions are welcome! Feel free to submit issues or pull requests on the [GitHub repository](https://github.com/janthmueller/kathekon).

---

## Acknowledgements

The Stoic quotes used in this project are sourced from [benhoneywill/stoic-quotes](https://github.com/benhoneywill/stoic-quotes).

---

## License

`kathekon` is licensed under the MIT License. See [LICENSE](LICENSE) for details.
