# kathekon

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

- **OpenAI Integration** *(Optional)*:
  - Generate thoughtful interpretations of quotes using OpenAI's GPT models.

- **Library Integration**:
  - Use `Quotes` as a Python library to integrate Stoic philosophy into your projects.

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
kathekon random --author "Marcus Aurelius"
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

### Example of a Resulting README

```markdown
<!--START_SECTION:quote-text-->
“Waste no more time arguing about what a good man should be. Be one.”
<!--END_SECTION:quote-text-->

<!--START_SECTION:quote-author-->
Marcus Aurelius
<!--END_SECTION:quote-author-->

<!--START_SECTION:quote-interpretation-->
When we spend too much time debating the meaning of virtue, we risk delaying its practice. This quote calls for immediate action: embody the qualities you admire in others and strive to be the person you aspire to be. In modern life, this might mean taking decisive steps to act with kindness and integrity rather than theorizing endlessly about morality.
<!--END_SECTION:quote-interpretation-->
```

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
daily_quote = quotes.get_daily_quote(interpretation="gpt+fallback")
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
for quote in quotes.get_quotes(author="Seneca", limit=3, interpretation="db"):
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

## License

`kathekon` is licensed under the MIT License. See [LICENSE](LICENSE) for details.

