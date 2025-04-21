"""
Updated CLI implementation with new diff and save commands.
"""
import time
import sys
import os
from pathlib import Path
import click


def lazy_load_dotenv():
    """Lazy load dotenv only when needed"""
    click.echo("🔑 Loading environment variables...")
    from dotenv import load_dotenv
    load_dotenv()
    click.echo("✅ Environment loaded")


def print_spinner(duration: float, message: str):
    """Display a simple spinner for the given duration"""
    spinner_chars = ['⣾', '⣽', '⣻', '⢿', '⡿', '⣟', '⣯', '⣷']
    start_time = time.time()
    i = 0

    # Print message with spinner
    while time.time() - start_time < duration:
        i = (i + 1) % len(spinner_chars)
        sys.stdout.write(f"\r{message} {spinner_chars[i]} ")
        sys.stdout.flush()
        time.sleep(0.1)

    # Clear the spinner line
    sys.stdout.write(f"\r{message} ✓ \n")
    sys.stdout.flush()


@click.group()
@click.option("--format", "fmt", type=click.Choice(['text', 'json']), default='text',
              help="Output format (text or json)")
@click.option("--include-responses", is_flag=True, help="Include full text responses in output")
@click.pass_context
def cli(ctx, fmt, include_responses):
    """promptpilot: manage and A/B test your prompts"""
    start_time = time.time()
    ctx.ensure_object(dict)

    # Store format preferences for later use - don't load formatters yet
    ctx.obj['format'] = fmt
    ctx.obj['include_responses'] = include_responses

    # Quick welcome message
    click.secho(f"🚀 PromptPilot v{get_version()}", fg='green')
    elapsed = time.time() - start_time
    if elapsed > 0.1:  # Only show timing for slower operations
        click.secho(f"Ready in {elapsed:.2f}s", fg='bright_black')


def get_version():
    """Get the current version from pyproject.toml if available"""
    try:
        import tomllib
        with open(Path(__file__).parent.parent.parent / "pyproject.toml", "rb") as f:
            data = tomllib.load(f)
            return data.get("project", {}).get("version", "0.0.1")  # Default if not found
    except (ImportError, FileNotFoundError):
        return "0.0.1"  # Fallback version


def get_formatter(ctx):
    """Lazy-load the appropriate formatter only when needed"""
    if not ctx.obj.get('formatter'):
        from promptpilot.formatters import TextFormatter, JSONFormatter
        fmt = ctx.obj.get('format', 'text')
        include_responses = ctx.obj.get('include_responses', False)

        if fmt == 'json':
            ctx.obj['formatter'] = JSONFormatter(include_responses=include_responses)
        else:
            ctx.obj['formatter'] = TextFormatter(include_responses=include_responses)

    return ctx.obj['formatter']


@cli.command()
@click.argument("prompt_name")
@click.option("--description", default="", help="Description for the new prompt")
@click.option("--author", default=None, help="Author name for metadata")
@click.pass_context
def init(ctx, prompt_name, description, author):
    """Initialize a new prompt YAML file in prompts/ directory"""
    # Lazy load dependencies
    click.echo("🔧 Setting up new prompt...")
    lazy_load_dotenv()

    prompts_dir = Path(os.getcwd()) / "prompts"
    prompts_dir.mkdir(exist_ok=True)
    file_path = prompts_dir / f"{prompt_name}.yml"

    if file_path.exists():
        click.secho(f"✋ Prompt '{prompt_name}' already exists.", fg='yellow')
        return

    metadata_author = author or os.getenv('USER', 'Unknown')
    today = time.strftime('%Y-%m-%d')

    click.echo("📝 Creating template...")
    boilerplate = f"""name: {prompt_name}
description: {description or 'Your prompt description'}
version: 1
author: {metadata_author}
created: {today}
updated: {today}

prompt: |
  # Your prompt template
  {{text}}

variables:
  - name: text
    description: Input text for the prompt
    required: true

metadata:
  recommended_models: []
  token_estimate:
    input_multiplier: 1.0
    base_tokens: 0

history: []
"""
    file_path.write_text(boilerplate)
    click.secho(f"✅ Initialized new prompt '{prompt_name}' at {file_path}", fg='green')

    # Also create a versions directory for this prompt
    versions_dir = prompts_dir / "versions" / prompt_name
    versions_dir.mkdir(parents=True, exist_ok=True)

    # Create first version backup
    from promptpilot.versioning import make_version_backup
    make_version_backup(prompt_name)

    click.echo(f"📂 Version history directory created at {versions_dir}")


@cli.command()
@click.argument("prompt_name")
@click.option("--save", is_flag=True, help="Save current state as a new version")
@click.pass_context
def diff(ctx, prompt_name, save):
    """Show diff between prompt versions or save a new version."""
    click.echo(f"🔍 Working with prompt '{prompt_name}'...")

    # Check if we're saving a new version
    if save:
        click.echo("💾 Saving current state as a new version...")
        from promptpilot.versioning import save_version

        if save_version(prompt_name):
            click.secho(f"✅ New version of '{prompt_name}' saved", fg='green')
        else:
            click.secho(f"❌ Failed to save version for '{prompt_name}'", fg='red')
        return

    # Show progress for diff operation
    click.echo("🔄 Computing differences between versions...")

    try:
        from promptpilot.versioning import get_diff
        diff_text = get_diff(prompt_name)

        if diff_text.startswith("Error:"):
            click.secho(f"⚠️ {diff_text}", fg='yellow')
        else:
            click.echo("✅ Diff computation complete")

            # Format the result
            result = {
                'type': 'diff_result',
                'prompt_name': prompt_name,
                'diff': diff_text
            }

            get_formatter(ctx).format_output(result)

    except Exception as e:
        click.secho(f"❌ Error getting diff: {e}", fg='red')


@cli.command()
@click.argument("prompt_name")
@click.option("--message", "-m", help="Optional message describing this version")
@click.pass_context
def save(ctx, prompt_name, message):
    """Save the current state of a prompt as a new version."""
    click.echo(f"💾 Saving current state of '{prompt_name}' as a new version...")

    try:
        from promptpilot.versioning import save_version

        if save_version(prompt_name):
            click.secho(f"✅ New version of '{prompt_name}' saved", fg='green')

            # Add commit message if provided
            if message:
                prompt_path = Path(f"prompts/{prompt_name}.yml")

                if prompt_path.exists():
                    try:
                        with open(prompt_path, 'r') as f:
                            import yaml
                            data = yaml.safe_load(f)

                        if 'history' in data and data['history']:
                            latest = data['history'][-1]
                            latest['message'] = message

                            with open(prompt_path, 'w') as f:
                                yaml.dump(data, f, default_flow_style=False, sort_keys=False)

                            click.echo(f"✓ Added message: '{message}'")
                    except Exception as e:
                        click.secho(f"⚠️ Could not add message: {e}", fg='yellow')
        else:
            click.secho(f"❌ Failed to save version for '{prompt_name}'", fg='red')

    except Exception as e:
        click.secho(f"❌ Error saving version: {e}", fg='red')


@cli.command()
@click.argument("prompt_name")
@click.option("--input", "input_file", type=click.Path(exists=True), required=True,
              help="Path to input file containing variables (e.g., text)")
@click.option("--provider", default=None, help="Provider to use (openai, claude, llama, hf)")
@click.option("--model", default=None, help="Model to use with the provider")
@click.pass_context
def abtest(ctx, prompt_name, input_file, provider, model):
    """Run A/B test comparing previous vs current prompt version"""
    # Start with minimal imports
    lazy_load_dotenv()

    # Show progress for each step
    click.echo(f"📥 Reading input from '{input_file}'...")
    with open(input_file, 'r') as f:
        input_text = f.read()
    click.echo(f"📄 Read {len(input_text)} characters")

    click.echo(f"📚 Loading prompt versions for '{prompt_name}'...")
    print_spinner(0.5, "Checking version history")

    # Lazy load components as needed
    try:
        from promptpilot.utils import load_prompt_versions
        prompt_a_content, prompt_b_content = load_prompt_versions(prompt_name)
        click.echo("✓ Loaded prompt templates")

        click.echo("🔧 Creating Prompt objects...")
        from promptpilot.models import Prompt
        prompt_a = Prompt(name=f"{prompt_name}_previous", template=prompt_a_content, version=1)
        prompt_b = Prompt(name=f"{prompt_name}_current",  template=prompt_b_content, version=2)

        provider_name = provider or "openai"
        click.echo(f"⚙️ Initializing {provider_name} provider...")
        print_spinner(0.8, f"Setting up {provider_name}")

        try:
            from promptpilot.providers import get_provider
            provider_instance = get_provider(provider, model)

            click.echo("🚀 Running A/B test...")
            from promptpilot.runner import ABTestRunner
            runner = ABTestRunner(
                provider=provider_instance,
                formatter=get_formatter(ctx)
            )

            # Show loading indicator for API requests which might take time
            print_spinner(1.0, "Sending request to variant A")
            print_spinner(1.0, "Sending request to variant B")
            print_spinner(0.5, "Comparing results")

            result = runner.run_test(
                prompt_a=prompt_a,
                prompt_b=prompt_b,
                variables={"text": input_text},
                include_responses=ctx.obj.get('include_responses', False)
            )

            click.secho("✅ A/B test completed!", fg='green')
            runner.display_results(result)

        except Exception as e:
            click.secho(f"❌ Error: {e}", fg='red')
            error_result = {'type': 'error', 'error': str(e)}
            get_formatter(ctx).format_output(error_result)

    except Exception as e:
        click.secho(f"❌ Error loading prompts: {e}", fg='red')


"""
Fixed list command to avoid naming conflict with built-in list() function.
"""

@cli.command(name="list")
@click.argument("prompt_name", required=False)
@click.pass_context
def list_prompts(ctx, prompt_name):
    """List available prompts or versions of a specific prompt."""
    prompts_dir = Path(os.getcwd()) / "prompts"

    if not prompts_dir.exists():
        click.secho("❌ No prompts directory found. Use 'promptpilot init' to create your first prompt.", fg='red')
        return

    if prompt_name:
        # List versions of a specific prompt
        click.echo(f"📋 Versions of prompt '{prompt_name}':")

        # Check YAML file
        prompt_file = prompts_dir / f"{prompt_name}.yml"
        if not prompt_file.exists():
            click.secho(f"❌ Prompt '{prompt_name}' not found.", fg='red')
            return

        # Check for versions directory
        versions_dir = prompts_dir / "versions" / prompt_name
        if versions_dir.exists():
            version_files = sorted(
                [(f, os.path.getmtime(f)) for f in versions_dir.glob("*.yml")],
                key=lambda x: x[1],
                reverse=True
            )

            if version_files:
                click.secho("Version history:", fg='green')
                for i, (path, timestamp) in enumerate(version_files):
                    time_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp))
                    click.echo(f"{i+1}. {path.name} - {time_str}")
            else:
                click.echo("No saved versions found in versions directory.")

        # Check YAML history
        try:
            import yaml
            with open(prompt_file, 'r') as f:
                data = yaml.safe_load(f)

            if 'history' in data and data['history']:
                click.secho("\nYAML history entries:", fg='green')
                for i, entry in enumerate(reversed(data['history'])):
                    message = f" - {entry.get('message', 'No message')}" if 'message' in entry else ""
                    click.echo(f"{i+1}. Version {entry.get('version', '?')} ({entry.get('date', 'unknown')}){message}")
            else:
                click.echo("No history entries in YAML file.")

            # Show current version
            click.secho(f"\nCurrent version: {data.get('version', 1)}", fg='blue')
            click.echo(f"Last updated: {data.get('updated', 'unknown')}")

        except Exception as e:
            click.secho(f"❌ Error reading YAML: {e}", fg='red')

    else:
        # List all available prompts
        click.echo("📋 Available prompts:")

        prompt_files = sorted(prompts_dir.glob("*.yml"))
        if not prompt_files:
            click.echo("No prompts found. Use 'promptpilot init <n>' to create one.")
            return

        for i, prompt_file in enumerate(prompt_files):
            name = prompt_file.stem
            try:
                import yaml
                with open(prompt_file, 'r') as f:
                    data = yaml.safe_load(f)

                desc = data.get('description', 'No description')
                version = data.get('version', 1)
                click.echo(f"{i+1}. {name} (v{version}) - {desc}")
            except Exception:
                click.echo(f"{i+1}. {name} - Could not read metadata")


if __name__ == "__main__":
    cli()
