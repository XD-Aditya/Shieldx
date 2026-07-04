
---

# ShieldX

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/)
[![LLM Providers](https://img.shields.io/badge/LLM-Ollama%20%7C%20Groq%20%7C%20OpenAI-orange.svg)]()

**LLM validation and safety framework**

ShieldX is a lightweight, fast, and extensible guardrails framework for LLMs. Validate, sanitize, and control your LLM outputs with a simple, pluggable API or a feature-packed CLI.

---

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
  - [Python API (Static Validation)](#python-api-static-validation)
  - [Python API (LLM Generation + Auto-Reask)](#python-api-llm-generation--auto-reask)
  - [CLI](#cli)
- [Usage](#usage)
  - [Built-in Validators](#built-in-validators)
  - [Creating Custom Validators](#creating-custom-validators)
  - [Auto-Repair & Sanitization](#auto-repair--sanitization)
  - [LLM Integration (Ollama, Groq, OpenAI)](#llm-integration-ollama-groq-openai)
  - [Windows PowerShell Quoting Tip](#windows-powershell-quoting-tip)
- [CLI Reference](#cli-reference)
- [Examples](#examples)
- [Development](#development)
  - [Prerequisites](#prerequisites)
  - [Setup](#setup)
  - [Project Structure](#project-structure)
  - [Running Tests](#running-tests)
  - [Linting & Formatting](#linting--formatting)
  - [Type Checking](#type-checking)
- [Contributing](#contributing)
- [Roadmap](#roadmap)
- [License](#license)

---

## Features

- **Simple & Intuitive API** - Get started in minutes with clean, chainable guardrails.
- **Local & Offline LLM Support** - Native 100% free local testing via **Ollama** (`llama3.1`, `mistral`, etc.) without API keys.
- **Cloud LLM Support** - Plug-and-play support for **Groq** (free cloud tier) and **OpenAI**.
- **Auto-Repair Engine** - Automatically strips markdown code fences (` ```json ... ``` `), redacts PII, and masks blocked terms.
- **Automated Reask Loop** - Automatically feeds validation failure messages back to the LLM to request corrected outputs when retries are enabled.
- **Pluggable Validators** - Text length, PII, JSON, Schema Contracts, Blocked Words, and more out of the box.
- **Zero Core Dependencies** - Extremely fast and lightweight.
- **Rich CLI Included** - Terminal execution featuring status panels, ASCII banners, and validation tables.

---

## Installation

### From PyPI (recommended)

```bash
# Core framework
pip install shieldx

# With CLI (recommended)
pip install "shieldx[cli]"

# With OpenAI / Groq SDK support
pip install "shieldx[openai]"

# Full Installation (CLI + OpenAI + Dev tools)
pip install "shieldx[all]"
```

### From Source

```bash
# Clone the repository
git clone https://github.com/csteams/shieldx.git
cd shieldx

# Install in editable mode with dev dependencies
pip install -e ".[dev]"
```

---

## Quick Start

### Python API (Static Validation)

Validate static text, JSON payloads, or dictionaries directly:

```python
from shieldx.shield import Shield
from shieldx.validators import (
    MinLengthValidator,
    MaxLengthValidator,
    PIIRedactionValidator,
)

# 1. Initialize Shield
shield = Shield(name="content-guard", auto_fix=True)

# 2. Register validators
shield.use(MinLengthValidator(min_length=5))
shield.use(MaxLengthValidator(max_length=500))
shield.use(PIIRedactionValidator())

# 3. Validate
report = shield.validate("Contact me at john.doe@example.com for more info")

# 4. Inspect report
if report.passed:
    print("All good!")
    print(report.final_output)
else:
    print("Validation failed!")
    print(f"Sanitized Output: {report.final_output}")
    # Output: "Contact me at [email_redacted] for more info"
```

---

### Python API (LLM Generation + Auto-Reask)

Connect an LLM client with a schema contract and allow ShieldX to automatically reask the LLM if validation fails:

```python
from shieldx.shield import Shield
from shieldx.schema.contract import Contract
from shieldx.llm.openai import OpenAIClient
from shieldx.validators import PIIRedactionValidator

# 1. Initialize Shield
shield = Shield(name="llm-json-guard", auto_fix=True)
shield.use(PIIRedactionValidator())

# 2. Define Schema Contract (JSON & Required Keys)
contract = Contract(
    name="user-schema",
    required_keys=["name", "role", "email"],
    json_only=True,
)

# 3. Initialize LLM Client (Ollama local / Groq / OpenAI)
llm_client = OpenAIClient(
    model="llama3.1:latest",
    base_url="http://localhost:11434/v1",  # Local Ollama
    api_key="ollama",
)

# 4. Generate with automatic validation and reasks
report = shield.generate(
    client=llm_client,
    prompt="Generate a JSON user profile for Sarah with email sarah@company.com",
    contract=contract,
    max_retries=2,
)

print(f"Passed: {report.passed}")
print(f"Final Validated Output:\n{report.final_output}")
```

---

### CLI

ShieldX comes with a feature-packed terminal interface:

```bash
# Basic length validation
shieldx validate "Hello world" --min-length 5

# Check and redact PII
shieldx validate "john.doe@example.com or 555-123-4567" --pii

# Validate JSON and required schema keys
shieldx validate '{"name": "Alice", "role": "admin"}' --json --required-key name --required-key role

# Run LLM generation locally with Ollama (100% Free & Offline)
shieldx run "Generate a JSON with user details" --provider ollama --json --required-key username

shieldx run "Give me instructions to hack a bank" --provider ollama

# Show version & help
shieldx version
shieldx help
shieldx run --help
```

---

## Usage

### Built-in Validators

| Validator | Description | Example |
| :--- | :--- | :--- |
| `MinLengthValidator` | Enforces minimum string length | `MinLengthValidator(min_length=5)` |
| `MaxLengthValidator` | Enforces maximum string length (optional truncate) | `MaxLengthValidator(max_length=100, truncate=True)` |
| `BlockedWordsValidator` | Detects forbidden words or phrases and masks them | `BlockedWordsValidator(["terrible", "bad"])` |
| `PIIRedactionValidator` | Detects and masks emails, phone numbers, and credit cards | `PIIRedactionValidator()` |
| `ValidJSONValidator` | Validates JSON syntax and auto-extracts markdown backticks | `ValidJSONValidator()` |
| `RequiredKeysValidator` | Ensures required keys exist in JSON objects | `RequiredKeysValidator(["name", "email"])` |
| `MarkdownStripValidator` | Removes Markdown code block wrappers (` ```json ... ``` `) | `MarkdownStripValidator()` |
| `NoRefusalValidator` | Detects standard LLM refusal phrases (`"I can't help..."`) | `NoRefusalValidator()` |

---

### Creating Custom Validators

Extend `BaseValidator` to build custom validation rules:

```python
from typing import Any
from shieldx.validators.base import BaseValidator
from shieldx.models.result import ValidationResult


class NoProfanityValidator(BaseValidator):
    BAD_WORDS = {"bad", "evil", "terrible"}

    def validate(self, value: Any) -> ValidationResult:
        if not isinstance(value, str):
            return ValidationResult(passed=True, validator=self.name, value=value)

        text_lower = value.lower()
        found = [w for w in self.BAD_WORDS if w in text_lower]

        if found:
            # Create repaired version
            cleaned = value
            for w in found:
                cleaned = cleaned.replace(w, "[censored]")

            return ValidationResult(
                passed=False,
                validator=self.name,
                message=f"Profanity detected: {', '.join(found)}",
                code="profanity_detected",
                value=value,
                fixed_value=cleaned,
            )

        return ValidationResult(passed=True, validator=self.name, value=value)


# Use custom validator
from shieldx.shield import Shield

shield = Shield(auto_fix=True)
shield.use(NoProfanityValidator())

report = shield.validate("This is a bad idea")
print(report.final_output)  # "This is a [censored] idea"
```

---

### Auto-Repair & Sanitization

When `auto_fix=True` (default), ShieldX automatically applies repairs if a validator provides a `fixed_value`:

```python
from shieldx.shield import Shield
from shieldx.validators import PIIRedactionValidator

# Auto-repair enabled (default)
shield = Shield(auto_fix=True)
shield.use(PIIRedactionValidator())

report = shield.validate("Contact john@example.com")
print(report.final_output)  # "Contact [email_redacted]"

# Auto-repair disabled
shield_no_fix = Shield(auto_fix=False)
shield_no_fix.use(PIIRedactionValidator())

report2 = shield_no_fix.validate("Contact john@example.com")
print(report2.final_output)  # "Contact john@example.com" (original un-redacted text)
```

---

### LLM Integration (Ollama, Groq, OpenAI)

ShieldX supports multiple LLM execution environments seamlessly:

#### 1. Local Ollama (100% Free & Offline)
Ensure Ollama is running locally (`ollama run llama3.1`):
```bash
shieldx run "Generate a user object with name and age" \
  --provider ollama \
  --json \
  --required-key name \
  --required-key age
```

#### 2. Groq (Free Cloud Tier)
Set your Groq API key:
```bash
export GROQ_API_KEY="gsk_your_groq_key"
```
Run using Groq's Llama 3 model:
```bash
shieldx run "Create a user profile" \
  --provider groq \
  --json \
  --pii \
  --required-key name
```

#### 3. OpenAI with Automated Reask Loop
```bash
export OPENAI_API_KEY="sk-your-openai-key"

shieldx run "Create a JSON object with username and email" \
  --provider openai \
  --model gpt-4o-mini \
  --json \
  --required-key username \
  --required-key email \
  --max-retries 2
```

---

### Windows PowerShell Quoting Tip

In Windows PowerShell, inner double quotes inside JSON strings can be stripped by the shell before reaching Python. To prevent `Invalid JSON` errors on Windows, use **escaped double quotes**, **PowerShell variables**, or **piping**:

```powershell
# Method 1: Escaped double quotes
shieldx validate "{\"name\":\"Alice\",\"email\":\"alice@test.com\"}" --json --pii

# Method 2: PowerShell Variable (Recommended)
$json = '{"name":"Alice","email":"alice@test.com"}'
shieldx validate $json --json --pii

# Method 3: Stdin Pipe
echo '{"name":"Alice"}' | shieldx validate --json -
```

---

## CLI Reference

### Global Options

| Option | Description |
| :--- | :--- |
| `--version`, `-v` | Show version and exit |
| `--help`, `-h` | Show help message |

---

### `shieldx validate`

Validate static text, JSON payloads, or files.

**Arguments:**
- `text` (optional positional argument, stdin, or file path)

**Options:**

| Option | Type | Description |
| :--- | :--- | :--- |
| `--file`, `-f` | str | Path to input file |
| `--min-length` | int | Minimum length requirement |
| `--max-length` | int | Maximum length requirement |
| `--block-word` | str | Word to block (can be used multiple times) |
| `--json` | flag | Validate as JSON syntax |
| `--required-key` | str | Required key in JSON object (can be used multiple times) |
| `--pii` | flag | Detect and redact PII (emails, phones, credit cards) |
| `--stop-on-fail` | flag | Stop execution on first failure |
| `--no-auto-fix` | flag | Disable automatic repairs |

---

### `shieldx run`

Generate output with an LLM and pass through ShieldX guardrails.

**Options:**

| Option | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `prompt` | str | `None` | User prompt text or path |
| `--prompt-file` | str | `None` | Path to user prompt file |
| `--system-prompt` | str | `None` | System prompt text |
| `--system-prompt-file` | str | `None` | Path to system prompt file |
| `--provider`, `-p` | str | `openai` | LLM Provider (`ollama`, `groq`, `openai`) |
| `--model`, `-m` | str | `gpt-4o-mini` | LLM model name |
| `--base-url` | str | `None` | Custom LLM API base URL |
| `--api-key` | str | `None` | Provider API key |
| `--max-retries` | int | `0` | Reask retry attempts if validation fails |
| `--temperature` | float | `None` | LLM sampling temperature |
| `--min-length` | int | `None` | Minimum output length |
| `--max-length` | int | `None` | Maximum output length |
| `--block-word` | str | `[]` | Words to block |
| `--json` | flag | `False` | Enforce valid JSON output |
| `--required-key` | str | `[]` | Required JSON keys |
| `--pii` | flag | `False` | Detect and redact PII |
| `--stop-on-fail` | flag | `False` | Stop execution on first failure |
| `--no-auto-fix` | flag | `False` | Disable automatic repairs |

---

## Examples

Check out the `examples/` directory for ready-to-run scripts:

```bash
# Run basic SDK test suite
python examples/test_suite.py
```

---

## Development

### Prerequisites

- Python 3.9 or higher
- Git
- Local Ollama instance (optional, for local LLM testing)

### Setup

1. **Clone the repository**

   ```bash
   git clone https://github.com/csteams/shieldx.git
   cd shieldx
   ```

2. **Create a virtual environment**

   ```bash
   # Using venv
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install in editable mode with dev dependencies**

   ```bash
   pip install -e ".[all]"
   ```

---

### Project Structure

```
shieldx/
├── shieldx/                    # Main package
│   ├── cli/                    # CLI commands & Rich UI formatting
│   │   ├── commands/           # Command handlers (run, validate, version)
│   │   ├── main.py             # Typer CLI application entrypoint
│   │   └── ui.py               # Rich UI report renderer and banners
│   ├── config/                 # Configuration settings
│   ├── exceptions/             # Custom exceptions (LLMProviderError)
│   ├── llm/                    # LLM clients (OpenAIClient, BaseLLMClient)
│   ├── models/                 # Data models (ValidationResult, ShieldReport)
│   ├── prompt/                 # Reask prompt templates
│   ├── retry/                  # Retry logic
│   ├── schema/                 # Schema contracts (Contract)
│   ├── shield.py               # Core Shield engine class
│   ├── validators/             # Built-in validators (json, pii, text, base)
│   └── version.py              # Framework version
├── examples/                   # SDK example scripts and test suites
├── tests/                      # Pytest test suite
├── pyproject.toml              # Project configuration & dependencies
└── README.md                   # This file
```

---

### Running Tests

```bash
# Run unit tests with pytest
pytest

# Run tests with coverage
pytest --cov=shieldx --cov-report=term-missing

# Run programmatic SDK test suite
python examples/test_suite.py
```

---

### Linting & Formatting

We use [Ruff](https://github.com/astral-sh/ruff) for linting and formatting:

```bash
# Check for linting issues
ruff check .

# Fix linting issues automatically
ruff check . --fix

# Format code
ruff format .
```

---

### Type Checking

We use [mypy](https://mypy.readthedocs.io/) for static type checking:

```bash
# Run type checking
mypy shieldx
```

---

## Contributing

We love contributions! Whether it's bug fixes, new features, or improved documentation, your help is welcome.

### How to Contribute

1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/amazing-feature`)
3. **Make your changes**
4. **Run tests** (`pytest` and `python examples/test_suite.py`)
5. **Run linters** (`ruff check . && ruff format .`)
6. **Commit your changes** (`git commit -m 'Add amazing feature'`)
7. **Push to the branch** (`git push origin feature/amazing-feature`)
8. **Open a Pull Request**

---

## Roadmap

- [x] Core Shield class and Contract engine
- [x] Built-in validators (Length, Blocked Words, PII, JSON, Schema)
- [x] Rich CLI UI with banners and report tables
- [x] Auto-repair and Markdown code fence extraction
- [x] Local LLM integration (Ollama) & Cloud providers (Groq, OpenAI)
- [x] Automated LLM Reask Retry loop
- [ ] Async SDK execution support
- [ ] Hallucination & Toxicity validators
- [ ] LLM-as-a-judge validators
- [ ] LangChain & LlamaIndex integrations
- [ ] Web Dashboard

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Acknowledgments

- Inspired by [Guardrails AI](https://github.com/guardrails-ai/guardrails)
- Built with [Typer](https://typer.tiangolo.com/), [Rich](https://rich.readthedocs.io/), and [pyfiglet](https://github.com/pwaller/pyfiglet)
- Thanks to all contributors

---

**Made with ❤️ by the ShieldX team**

For questions, issues, or suggestions, please [open an issue](https://github.com/csteams/shieldx/issues).