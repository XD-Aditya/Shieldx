from __future__ import annotations

import os
from pathlib import Path
from typing import List, Optional
from shieldx.validators.markdown import MarkdownStripValidator
from shieldx.validators.refusal import RefusalDetectorValidator
from shieldx.cli.ui import console, print_banner, print_error, render_report
from shieldx.schema.contract import Contract
from shieldx.shield import Shield
from shieldx.validators.json import RequiredKeysValidator, ValidJSONValidator
from shieldx.validators.pii import PIIRedactionValidator
from shieldx.validators.text import (
    BlockedWordsValidator,
    MaxLengthValidator,
    MinLengthValidator,
)


def _get_llm_client(provider: str, model: str, api_key: Optional[str] = None, **kwargs):
    """
    Get LLM client based on provider.
    """
    if provider == "ollama":
        from shieldx.llm.ollama import OllamaClient
        return OllamaClient(model=model, **kwargs)
    
    elif provider == "openai":
        from shieldx.llm.openai import OpenAIClient
        return OpenAIClient(api_key=api_key, model=model, **kwargs)
    
    elif provider == "groq":
        from shieldx.llm.openai import OpenAIClient
        return OpenAIClient(api_key=api_key, model=model, **kwargs)
    
    else:
        raise ValueError(f"Unknown provider: {provider}. Use: ollama, openai, groq")


def _read_text_or_file(
    text: Optional[str],
    file_path: Optional[str],
    label: str,
) -> str:
    if text is not None:
        return text

    if file_path is not None:
        return Path(file_path).read_text(encoding="utf-8")

    raise ValueError(f"Provide either --{label} or --{label}-file.")


def run_command(
    prompt: Optional[str] = None,
    prompt_file: Optional[str] = None,
    system_prompt: Optional[str] = None,
    system_prompt_file: Optional[str] = None,
    api_key: Optional[str] = None,
    model: str = "llama3.1",
    provider: str = "ollama",
    max_retries: int = 0,
    temperature: Optional[float] = None,
    min_length: Optional[int] = None,
    max_length: Optional[int] = None,
    block_words: Optional[List[str]] = None,
    require_json: bool = False,
    required_keys: Optional[List[str]] = None,
    redact_pii: bool = False,
    stop_on_fail: bool = False,
    no_auto_fix: bool = False,
) -> int:
    try:
        user_prompt = _read_text_or_file(prompt, prompt_file, "prompt")
        final_system_prompt = None
        if system_prompt is not None or system_prompt_file is not None:
            final_system_prompt = _read_text_or_file(
                system_prompt, system_prompt_file, "system-prompt"
            )
    except Exception as exc:
        print_error(str(exc))
        return 1

    # Get API key for non-Ollama providers
    resolved_api_key = api_key
    if provider != "ollama":
        resolved_api_key = resolved_api_key or os.getenv(f"{provider.upper()}_API_KEY") or os.getenv("OPENAI_API_KEY")
        if not resolved_api_key:
            print_error(f"Missing API key for {provider}. Use --api-key or set {provider.upper()}_API_KEY.")
            return 1

    # Build LLM kwargs
    llm_kwargs = {}
    if temperature is not None:
        llm_kwargs["temperature"] = temperature

    # Get LLM client based on provider
    try:
        client = _get_llm_client(provider, model, resolved_api_key, **llm_kwargs)
    except Exception as exc:
        print_error(str(exc))
        return 1

    # Setup Shield
    shield = Shield(
        name="shieldx-run",
        auto_fix=not no_auto_fix,
        stop_on_fail=stop_on_fail,
    )

    if min_length is not None:
        shield.use(MinLengthValidator(min_length))

    if max_length is not None:
        shield.use(MaxLengthValidator(max_length))

    if block_words:
        shield.use(BlockedWordsValidator(block_words))

    if redact_pii:
        shield.use(PIIRedactionValidator())

    shield.use(RefusalDetectorValidator())

    if require_json or required_keys:
        shield.use(MarkdownStripValidator())
    
    if require_json and not required_keys:
        shield.use(ValidJSONValidator())

    if required_keys and not require_json:
        shield.use(RequiredKeysValidator(required_keys))

    if require_json or required_keys:
        shield.use(MarkdownStripValidator())

    contract = None
    if require_json or required_keys:
        contract = Contract(
            name="shieldx-cli-contract",
            required_keys=required_keys or [],
            json_only=(require_json or bool(required_keys)),
        )

    try:
        print_banner()
        console.print(f"[bold cyan]Provider:[/bold cyan] {provider} | [bold cyan]Model:[/bold cyan] {model}")
        with console.status("[bold cyan]Generating, validating, and repairing if needed...[/bold cyan]", spinner="dots"):
            report = shield.generate(
                client=client,
                prompt=user_prompt,
                system_prompt=final_system_prompt,
                contract=contract,
                max_retries=max_retries,
            )

        render_report(report)
        return 0 if report.passed else 1

    except Exception as exc:
        print_error(str(exc))
        return 1