"""
Updated utils module with better version loading and management.
"""
import warnings
from pathlib import Path
import yaml
import os
import click
import time


def load_prompt_versions(prompt_name: str):
    """
    Return (previous, current) content of prompt file.

    Enhanced implementation that uses multiple strategies:
    1. First try to load from version files in prompts/versions/
    2. If that fails, try loading from YAML history
    3. If both fail, return default templates as fallback
    """
    prompt_path = Path(f"prompts/{prompt_name}.yml")

    # Check if prompt exists
    if not prompt_path.exists():
        click.echo(f"⚠️ Prompt file not found: {prompt_path}")
        return _get_default_templates()

    # Current prompt content
    try:
        with open(prompt_path, 'r') as f:
            prompt_data = yaml.safe_load(f)

        current_template = prompt_data.get('prompt', '')
        current_version = prompt_data.get('version', 1)
    except Exception as e:
        click.echo(f"⚠️ Error reading prompt file: {e}")
        return _get_default_templates()

    # Strategy 1: Version files
    versions_dir = Path(f"prompts/versions/{prompt_name}")
    if versions_dir.exists():
        try:
            # Find all version files
            versions = sorted(
                [(f, os.path.getmtime(f)) for f in versions_dir.glob("*.yml")],
                key=lambda x: x[1],
                reverse=True
            )

            if len(versions) >= 2:
                # We have at least two versions - get the second most recent one
                with open(versions[1][0], 'r') as f:
                    prev_data = yaml.safe_load(f)

                if prev_data and 'prompt' in prev_data:
                    click.echo("✅ Loaded previous version from version files")
                    return prev_data['prompt'], current_template

            elif len(versions) == 1:
                # Only one version file exists, we need to create a backup of current
                click.echo("⚠️ Only one version file found, creating a backup of current version")
                from promptpilot.versioning import make_version_backup
                make_version_backup(prompt_name)

                # Return two copies of current for comparison
                return current_template, current_template
        except Exception as e:
            click.echo(f"⚠️ Error reading version files: {e}")
            # Continue to next strategy

    # Strategy 2: YAML history
    try:
        hist = prompt_data.get('history', [])
        if hist and current_version > 1:
            # Find the previous version in history
            prev = next((h for h in hist if h.get('version') == current_version - 1), None)

            if prev and 'prompt' in prev:
                click.echo("✅ Loaded previous version from YAML history")
                return prev['prompt'], current_template
    except Exception as e:
        click.echo(f"⚠️ Error reading YAML history: {e}")
        # Continue to fallback strategy

    # Strategy 3: Git history (try as a last resort)
    try:
        from git import Repo
        repo = Repo('.')
        path = f"prompts/{prompt_name}.yml"

        try:
            # Try to get previous version from git
            prev_content = repo.git.show(f"HEAD~1:{path}")

            try:
                prev_data = yaml.safe_load(prev_content)
                if prev_data and 'prompt' in prev_data:
                    click.echo("✅ Loaded previous version from Git history")
                    return prev_data['prompt'], current_template
            except Exception:
                pass  # YAML parsing failed, continue to fallback
        except Exception:
            pass  # Git command failed, continue to fallback
    except (ImportError, Exception):
        # Git not available or other error
        pass

    # Strategy 4: Fallback - create new version backup and return defaults
    click.echo("⚠️ No previous version found, creating backup and using defaults")

    # Create a backup of the current version for future comparisons
    try:
        from promptpilot.versioning import make_version_backup
        make_version_backup(prompt_name)
    except Exception:
        pass

    # Return default templates (but use current as the second one if available)
    defaults = _get_default_templates()
    if current_template:
        return defaults[0], current_template
    else:
        return defaults


def _get_default_templates():
    """Return default templates for fallback"""
    a = """
    Summarize the following text in about 3 paragraphs:
    
    {text}
    """
    b = """
    Create a concise summary of the following text. Focus on the main points
    and key details. Use about 3 paragraphs and make it engaging:
    
    {text}
    """
    return a, b


def get_formatter(ctx):
    """
    Lazy-load the appropriate formatter only when needed.
    This is used by multiple CLI commands.
    """
    if not ctx.obj.get('formatter'):
        from promptpilot.formatters import TextFormatter, JSONFormatter
        fmt = ctx.obj.get('format', 'text')
        include_responses = ctx.obj.get('include_responses', False)

        if fmt == 'json':
            ctx.obj['formatter'] = JSONFormatter(include_responses=include_responses)
        else:
            ctx.obj['formatter'] = TextFormatter(include_responses=include_responses)

    return ctx.obj['formatter']


def create_versioned_prompt(prompt_name, template, version=1, author=None, description=None):
    """
    Create a new prompt file with version tracking enabled.

    Args:
        prompt_name: Name of the prompt
        template: Initial prompt template
        version: Initial version (default=1)
        author: Author name (default=current user)
        description: Prompt description

    Returns:
        Path to the created prompt file
    """
    prompts_dir = Path("prompts")
    prompts_dir.mkdir(exist_ok=True)

    versions_dir = prompts_dir / "versions" / prompt_name
    versions_dir.mkdir(parents=True, exist_ok=True)

    # Create prompt file
    file_path = prompts_dir / f"{prompt_name}.yml"

    if file_path.exists():
        raise FileExistsError(f"Prompt '{prompt_name}' already exists at {file_path}")

    author = author or os.getenv('USER', 'Unknown')
    today = time.strftime('%Y-%m-%d')

    prompt_data = {
        "name": prompt_name,
        "description": description or "Your prompt description",
        "version": version,
        "author": author,
        "created": today,
        "updated": today,
        "prompt": template.strip(),
        "variables": [
            {
                "name": "text",
                "description": "Input text for the prompt",
                "required": True
            }
        ],
        "metadata": {
            "recommended_models": [],
            "token_estimate": {
                "input_multiplier": 1.0,
                "base_tokens": 0
            }
        },
        "history": []
    }

    with open(file_path, 'w') as f:
        yaml.dump(prompt_data, f, default_flow_style=False, sort_keys=False)

    # Create initial version backup
    from promptpilot.versioning import make_version_backup
    make_version_backup(prompt_name)

    return file_path
