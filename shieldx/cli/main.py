from __future__ import annotations

import json
import os
import sys
from typing import List, Optional

import typer
from rich.console import Console

from shieldx.cli.commands import run_command, validate_command, version_command
from shieldx.cli.ui import print_banner

app = typer.Typer(
    name="shieldx",
    add_completion=False,  
    help="ShieldX CLI - LLM validation and safety framework",
    no_args_is_help=True,
    rich_markup_mode="rich",
)
console = Console()


def smart_fix_json(text: str) -> str:
    """
    Fix shell quoting issues, especially PowerShell's mangling of JSON.
    Converts '{key:value}' -> {"key":"value"}
    """
    import re
    
    # If it's already valid JSON, return as-is
    try:
        json.loads(text)
        return text
    except json.JSONDecodeError:
        pass
    
    # Strip outer single quotes (PowerShell often wraps with these)
    if text.startswith("'") and text.endswith("'"):
        text = text[1:-1]
    
    # If it looks like JSON objects/arrays but has no double quotes, 
    # PowerShell likely stripped them. Try to reconstruct.
    if ('{' in text or '[' in text) and '"' not in text:
        # Step 1: Quote unquoted keys (word before :)
        # Use positive lookahead to find words followed by :
        text = re.sub(r'([{,]\s*)([a-zA-Z_]\w*)(\s*:)', r'\1"\2"\3', text)
        
        # Step 2: Quote unquoted string values
        def quote_value(match):
            colon = match.group(1)  # ': ' or ':'
            val = match.group(2).strip()
            end = match.group(3)    # ',' or '}' or ']'
            
            # Don't quote if it's a special value (true, false, null, number)
            if val.lower() in ('true', 'false', 'null'):
                return f'{colon}{val}{end}'
            try:
                float(val)
                return f'{colon}{val}{end}'
            except ValueError:
                pass
            
            # Quote the value
            return f'{colon}"{val}"{end}'
        
        # Match values: colon, value, then comma/bracket/end
        text = re.sub(r'(:\s*)([^,\}\]\s]+)(\s*[,}\]])', quote_value, text)
        
        # Try to validate the fix
        try:
            json.loads(text)
            return text
        except json.JSONDecodeError:
            pass  # Return original text if fix failed, let validator report error
    
    return text


def get_input_text(text: Optional[str], file: Optional[str]) -> str:
    """
    Get input text from various sources (argument, file, stdin).
    """
    # If text is "-" or not provided, try stdin
    if text == "-" or (not text and not file):
        if not sys.stdin.isatty():
            # Reading from pipe
            return sys.stdin.read().strip()
        elif not text and not file:
            # Interactive mode
            console.print("[dim]Enter text to validate (Ctrl+D/Ctrl+Z when done):[/dim]")
            return sys.stdin.read().strip()
    
    # If text looks like a file path and exists, read it
    if text and not file and os.path.exists(text):
        with open(text, 'r', encoding='utf-8') as f:
            return f.read()
    
    # If file specified, read it
    if file:
        with open(file, 'r', encoding='utf-8') as f:
            return f.read()
    
    # Otherwise, use text directly but fix shell mangling
    if text:
        return smart_fix_json(text)
    
    raise typer.BadParameter("No input provided. Use TEXT argument, --file, or pipe via stdin.")


@app.command(help="Show ShieldX version")
def version() -> None:
    version_command()


@app.command(help="Validate text or JSON")
def validate(
    text: Optional[str] = typer.Argument(None, help="Text to validate, file path, or '-' for stdin"),
    file: Optional[str] = typer.Option(None, "--file", "-f", help="Path to input file"),
    min_length: Optional[int] = typer.Option(None, "--min-length", help="Minimum length"),
    max_length: Optional[int] = typer.Option(None, "--max-length", help="Maximum length"),
    block_word: List[str] = typer.Option([], "--block-word", help="Words to block"),
    json: bool = typer.Option(False, "--json", help="Validate as JSON"),
    required_key: List[str] = typer.Option([], "--required-key", help="Required JSON keys"),
    pii: bool = typer.Option(False, "--pii", help="Detect and redact PII"),
    stop_on_fail: bool = typer.Option(False, "--stop-on-fail", help="Stop on first failure"),
    no_auto_fix: bool = typer.Option(False, "--no-auto-fix", help="Disable auto repair"),
    raw: bool = typer.Option(False, "--raw", help="Output raw JSON result"),
) -> None:
    """
    Validate text or JSON input.
    
    Examples:
        # Basic text
        shieldx validate "Hello world" --min-length 5
        
        # JSON (Windows PowerShell - use double quotes escaped)
        shieldx validate "{\\"name\\":\\"Alice\\"}" --json
        
        # JSON (Linux/Mac - use single quotes)
        shieldx validate '{"name":"Alice"}' --json
        
        # From file
        shieldx validate --file input.json --json
        
        # From stdin (pipe)
        echo '{"name":"Alice"}' | shieldx validate --json -
        
        # Interactive
        shieldx validate --json
    """
    try:
        input_text = get_input_text(text, file)
    except FileNotFoundError:
        console.print(f"[bold red]Error:[/bold red] File not found: {file or text}")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(1)
    
    # Call your existing command
    ret_code = validate_command(
        text=input_text,
        file=None,  # We already read the file
        min_length=min_length,
        max_length=max_length,
        block_words=block_word,
        require_json=json,
        required_keys=required_key,
        redact_pii=pii,
        stop_on_fail=stop_on_fail,
        no_auto_fix=no_auto_fix,
    )
    
    raise typer.Exit(ret_code)


@app.command(help="Generate with LLM and validate output")
def run(
    prompt: Optional[str] = typer.Argument(None, help="Prompt text, file path, or '-' for stdin"),
    prompt_file: Optional[str] = typer.Option(None, "--prompt-file", help="Path to prompt file"),
    system_prompt: Optional[str] = typer.Option(None, "--system-prompt", help="System prompt text"),
    system_prompt_file: Optional[str] = typer.Option(None, "--system-prompt-file", help="Path to system prompt file"),
    provider: str = typer.Option("ollama", "--provider", help="LLM provider: ollama, openai, groq"),
    api_key: Optional[str] = typer.Option(None, "--api-key", help="OpenAI API key"),
       model: str = typer.Option("llama3.1", "--model", help="LLM model name"),
    max_retries: int = typer.Option(0, "--max-retries", help="Retry attempts if validation fails"),
    temperature: Optional[float] = typer.Option(None, "--temperature", help="Sampling temperature"),
    min_length: Optional[int] = typer.Option(None, "--min-length", help="Minimum length"),
    max_length: Optional[int] = typer.Option(None, "--max-length", help="Maximum length"),
    block_word: List[str] = typer.Option([], "--block-word", help="Words to block"),
    json: bool = typer.Option(False, "--json", help="Validate as JSON"),
    required_key: List[str] = typer.Option([], "--required-key", help="Required JSON keys"),
    pii: bool = typer.Option(False, "--pii", help="Detect and redact PII"),
    stop_on_fail: bool = typer.Option(False, "--stop-on-fail", help="Stop on first failure"),
    no_auto_fix: bool = typer.Option(False, "--no-auto-fix", help="Disable auto repair"),
) -> None:
    """
    Generate with LLM and validate output.
    
    Examples:
        shieldx run "Write a JSON object with name and email" --json --required-key name
        shieldx run --prompt-file prompt.txt --json --pii
        cat prompt.txt | shieldx run --json -
    """
    try:
        input_prompt = get_input_text(prompt, prompt_file)
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(1)
    
    # Handle system prompt file
    sys_prompt = system_prompt
    if system_prompt_file:
        try:
            with open(system_prompt_file, 'r') as f:
                sys_prompt = f.read()
        except FileNotFoundError:
            console.print(f"[bold red]Error:[/bold red] System prompt file not found: {system_prompt_file}")
            raise typer.Exit(1)
    
    ret_code = run_command(
        prompt=input_prompt,
        prompt_file=None,
        system_prompt=sys_prompt,
        system_prompt_file=None,
        api_key=api_key,
        model=model,
        provider=provider,
        max_retries=max_retries,
        temperature=temperature,
        min_length=min_length,
        max_length=max_length,
        block_words=block_word,
        require_json=json,
        required_keys=required_key,
        redact_pii=pii,
        stop_on_fail=stop_on_fail,
        no_auto_fix=no_auto_fix,
    )
    raise typer.Exit(ret_code)


def main() -> int:
    # Handle 'shieldx help' syntax
    if len(sys.argv) > 1 and sys.argv[1] == "help":
        if len(sys.argv) == 2:
            sys.argv[1] = "--help"
        elif len(sys.argv) >= 3:
            cmd = sys.argv[2]
            sys.argv = [sys.argv[0], cmd, "--help"]
    
    if "--help" in sys.argv or "-h" in sys.argv:
        print_banner()
    
    try:
        app()
        return 0
    except SystemExit as e:
        return e.code or 0


if __name__ == "__main__":
    sys.exit(main())