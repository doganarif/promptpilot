"""
Enhanced versioning module with file-based version tracking - fixed exports.
"""
from pathlib import Path
import os
import yaml
import shutil
import time
import json
import click


# Make this function accessible for imports from other modules
def make_version_backup(prompt_name: str):
    """
    Make a backup of the current prompt version.

    Stores the backup in prompts/versions/{prompt_name}/v1_{timestamp}.yml
    """
    prompt_path = Path(f"prompts/{prompt_name}.yml")

    if not prompt_path.exists():
        click.echo(f"Warning: Cannot backup nonexistent file {prompt_path}")
        return

    # Create versions directory if it doesn't exist
    versions_dir = Path(f"prompts/versions/{prompt_name}")
    versions_dir.mkdir(parents=True, exist_ok=True)

    # Load the current file to get its version number
    try:
        with open(prompt_path, 'r') as f:
            prompt_data = yaml.safe_load(f)
        version = prompt_data.get('version', 1)
    except Exception:
        version = 1  # Default if we can't read the file

    # Create a timestamped version file
    timestamp = int(time.time())
    backup_path = versions_dir / f"v{version}_{timestamp}.yml"

    # Copy the file
    shutil.copy2(prompt_path, backup_path)
    click.echo(f"Version backup created: {backup_path}")


# Define _make_version_backup as an alias for backward compatibility
_make_version_backup = make_version_backup


def get_diff(prompt_name: str) -> str:
    """
    Return diff for prompt versions.

    This implementation tries multiple strategies to get version differences:
    1. Git history (if available)
    2. Manual version directory (prompts/versions/{prompt_name}/)
    3. YAML history section
    4. Create a new version if none exists
    """
    prompt_path = Path(f"prompts/{prompt_name}.yml")

    # Check if the prompt file exists
    if not prompt_path.exists():
        return f"Error: Prompt file '{prompt_path}' not found. Use 'promptpilot init {prompt_name}' to create it."

    # 1. Try Git first
    try:
        from git import Repo
        repo = Repo('.')
        try:
            return repo.git.diff('HEAD~1', 'HEAD', f"prompts/{prompt_name}.yml")
        except Exception as git_err:
            # Git error but don't return yet, try other methods
            click.echo(f"Note: Git diff unavailable ({git_err})")
    except ImportError:
        # Git package not installed - continue to other methods
        pass

    # 2. Check version directory
    versions_dir = Path(f"prompts/versions/{prompt_name}")
    if versions_dir.exists() and list(versions_dir.glob("*.yml")):
        # Find the two most recent versions
        versions = sorted(
            [(f, os.path.getmtime(f)) for f in versions_dir.glob("*.yml")],
            key=lambda x: x[1],
            reverse=True
        )

        if len(versions) >= 2:
            newest, second_newest = versions[0][0], versions[1][0]

            # Generate diff between the two files
            with open(second_newest, 'r') as f1, open(newest, 'r') as f2:
                old_content = f1.readlines()
                new_content = f2.readlines()

            diff_lines = []
            diff_lines.append(f"--- {os.path.basename(second_newest)}")
            diff_lines.append(f"+++ {os.path.basename(newest)}")

            # Simple diff: show removed lines with - and added lines with +
            for line in old_content:
                if line not in new_content:
                    diff_lines.append(f"- {line.rstrip()}")

            for line in new_content:
                if line not in old_content:
                    diff_lines.append(f"+ {line.rstrip()}")

            return "\n".join(diff_lines)
        else:
            # Only one version exists - make a copy for future diffs
            click.echo("Only one version found. Creating backup for future comparisons.")
            make_version_backup(prompt_name)
            return "No previous version to compare. This version has been saved for future comparisons."

    # 3. Check YAML history
    try:
        with open(prompt_path, 'r') as f:
            prompt_data = yaml.safe_load(f)

        hist = prompt_data.get('history', [])
        curr_version = prompt_data.get('version', 1)

        if hist and curr_version > 1:
            # Find the previous version in history
            prev = next((h for h in hist if h.get('version') == curr_version - 1), None)

            if prev and 'prompt' in prev:
                diff_lines = []
                diff_lines.append(f"--- Version {curr_version - 1}")
                diff_lines.append(f"+++ Version {curr_version}")

                # Split the prompts into lines for comparison
                old_lines = prev['prompt'].splitlines()
                new_lines = prompt_data['prompt'].splitlines()

                # Simple diff implementation
                for line in old_lines:
                    if line not in new_lines:
                        diff_lines.append(f"- {line}")

                for line in new_lines:
                    if line not in old_lines:
                        diff_lines.append(f"+ {line}")

                return "\n".join(diff_lines)
    except Exception as yaml_err:
        return f"Error reading YAML: {yaml_err}"

    # 4. No previous versions - create a backup for future diffs
    click.echo("No version history found. Creating backup for future comparisons.")
    make_version_backup(prompt_name)

    return "No previous version to compare. This version has been saved for future comparisons."


def save_version(prompt_name: str, increment: bool = True):
    """
    Save a new version of a prompt.

    Args:
        prompt_name: Name of the prompt
        increment: Whether to increment the version number
    """
    prompt_path = Path(f"prompts/{prompt_name}.yml")

    if not prompt_path.exists():
        click.echo(f"Error: Prompt file '{prompt_path}' not found")
        return False

    # Make a backup first
    make_version_backup(prompt_name)

    # Increment version if requested
    if increment:
        try:
            with open(prompt_path, 'r') as f:
                prompt_data = yaml.safe_load(f)

            current_version = prompt_data.get('version', 1)
            prompt_data['version'] = current_version + 1
            prompt_data['updated'] = time.strftime('%Y-%m-%d')

            # Add previous version to history
            if 'history' not in prompt_data:
                prompt_data['history'] = []

            # Copy current prompt to history before updating
            history_entry = {
                'version': current_version,
                'date': prompt_data.get('updated', time.strftime('%Y-%m-%d')),
                'prompt': prompt_data.get('prompt', '')
            }

            prompt_data['history'].append(history_entry)

            # Write back the updated file
            with open(prompt_path, 'w') as f:
                yaml.dump(prompt_data, f, default_flow_style=False, sort_keys=False)

            click.echo(f"✅ Prompt version incremented from {current_version} to {current_version + 1}")
            return True

        except Exception as e:
            click.echo(f"Error updating version: {e}")
            return False

    return True


# Export functions for use in other modules
__all__ = [
    'get_diff',
    'save_version',
    'make_version_backup',
]
