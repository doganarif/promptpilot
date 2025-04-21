# PromptPilot Usage Guide

This guide demonstrates the key workflows for using PromptPilot to manage and test your prompts.

## Getting Started

### Installation

```bash
pip install promptpilot
```

### Initialize Your First Prompt

```bash
promptpilot init summary --description "Summarize text in three paragraphs" --author "Your Name"
```

This creates a new prompt template at `prompts/summary.yml` and sets up version tracking.

## Prompt Version Management

PromptPilot offers a robust versioning system that works with or without Git. Here's how to use it:

### Creating a New Version

After modifying your prompt file, save it as a new version:

```bash
promptpilot save summary -m "Added instructions for better formatting"
```

This will:
1. Create a backup of the current file in `prompts/versions/summary/`
2. Increment the version number in the YAML file
3. Add the previous version to the history section
4. Include your commit message in the history

### Viewing Version History

List all versions of a prompt:

```bash
promptpilot list summary
```

Example output:
```
🚀 PromptPilot v0.0.1
📋 Versions of prompt 'summary':

Version history:
1. v2_1714042897.yml - 2025-04-21 14:34:57
2. v1_1714042811.yml - 2025-04-21 14:33:31

YAML history entries:
1. Version 1 (2025-04-21) - Initial version

Current version: 2
Last updated: 2025-04-21
```

### Comparing Versions

To see the differences between versions:

```bash
promptpilot diff summary
```

Example output:
```
🚀 PromptPilot v0.0.1
🔍 Working with prompt 'summary'...
🔄 Computing differences between versions...
✅ Diff computation complete
Test Results:
prompt_name: summary
diff: --- v1_1714042811.yml
+++ v2_1714042897.yml
- prompt: |
-   Summarize the following text in about 3 paragraphs:
-   
-   {text}
+ prompt: |
+   Create a concise summary of the following text. Focus on the main points
+   and key details. Use about 3 paragraphs and make it engaging:
+   
+   {text}
```

## Managing Multiple Prompts

### List All Prompts

See all available prompts:

```bash
promptpilot list
```

Example output:
```
🚀 PromptPilot v0.0.1
📋 Available prompts:
1. summary (v2) - Summarize text in three paragraphs
2. translation (v1) - Translate text between languages
```

### Create Additional Prompts

Create specialized prompts for different tasks:

```bash
promptpilot init translation --description "Translate text between languages"
```

## Prompt Testing and Optimization

### Running A/B Tests

Compare two versions of a prompt to see which is more efficient:

```bash
promptpilot abtest summary --input article.txt --provider openai
```

Example output:
```
🚀 PromptPilot v0.0.1
🔑 Loading environment variables...
✅ Environment loaded
📥 Reading input from 'article.txt'...
📄 Read 1542 characters
📚 Loading prompt versions for 'summary'...
Checking version history ✓ 
✓ Loaded prompt templates
🔧 Creating Prompt objects...
⚙️ Initializing openai provider...
Setting up openai ✓ 
🚀 Running A/B test...
Sending request to variant A ✓ 
Sending request to variant B ✓ 
Comparing results ✓ 
✅ A/B test completed!

==================================================
A/B TEST RESULTS
==================================================
Provider: openai

VARIANT A: summary_previous
Template:
  Summarize the following text in about 3 paragraphs:
  
  {text}
Tokens: 256

VARIANT B: summary_current
Template:
  Create a concise summary of the following text. Focus on the main points
  and key details. Use about 3 paragraphs and make it engaging:
  
  {text}
Tokens: 243

==================================================
RESULTS SUMMARY
Winner: Variant B
Token difference: 13
Savings percentage: 5.08%
Reason: Lower token usage
```

### Include Full Responses in Results

To see the actual generated text:

```bash
promptpilot abtest summary --input article.txt --provider openai --include-responses
```

### Testing with Different Providers

```bash
# Test with Claude
promptpilot abtest summary --input article.txt --provider claude --model claude-3-opus-20240229

# Test with HuggingFace models
promptpilot abtest summary --input article.txt --provider hf --model gpt2
```

## Complete Workflow Example

Here's a complete example of the prompt development lifecycle:

```bash
# 1. Create a new prompt template
promptpilot init report --description "Generate report from data"

# 2. Edit the prompt file at prompts/report.yml
# (Add your initial template)

# 3. Save the initial version
promptpilot save report -m "Initial version"

# 4. Run a test with sample data
promptpilot abtest report --input sample_data.txt --provider openai

# 5. Edit the prompt file again to make improvements
# (Modify the template based on test results)

# 6. Save the improved version
promptpilot save report -m "Added better structure and formatting instructions"

# 7. Compare versions to see your changes
promptpilot diff report

# 8. Test the new version
promptpilot abtest report --input sample_data.txt --provider openai --include-responses

# 9. View version history
promptpilot list report
```

## Tips for Effective Prompt Management

### Incremental Changes

Make small, focused changes between versions so you can isolate what works:

```bash
# Original version
promptpilot init email --description "Generate email responses"

# Edit prompts/email.yml with basic template
promptpilot save email -m "Basic email template"

# Edit to add tone instructions
promptpilot save email -m "Added professional tone instructions"

# Edit to add formatting guidelines
promptpilot save email -m "Added formatting guidelines"
```

### Using Input Files

Create dedicated input files for consistent testing:

```
inputs/
├── short_article.txt   # For quick tests
├── long_article.txt    # For stress testing
└── technical_paper.txt # For domain-specific testing
```

### JSON Output for Further Analysis

Export test results as JSON for further processing:

```bash
promptpilot abtest summary --input article.txt --format json > results.json
```

## Advanced Usage Patterns

### Batch Testing Script

Test multiple prompts with multiple providers:

```bash
#!/bin/bash
# test_all.sh

PROMPTS=("summary" "translation" "email")
PROVIDERS=("openai" "claude")
INPUT="sample.txt"

for prompt in "${PROMPTS[@]}"; do
  for provider in "${PROVIDERS[@]}"; do
    echo "Testing $prompt with $provider..."
    promptpilot abtest $prompt --input $INPUT --provider $provider --format json > "results_${prompt}_${provider}.json"
  done
done

echo "All tests completed!"
```

### Version Backup Script

Create scheduled backups of all your prompts:

```bash
#!/bin/bash
# backup_all.sh

cd /path/to/your/project
PROMPTS=$(ls prompts/*.yml | xargs -n1 basename | cut -d. -f1)

for prompt in $PROMPTS; do
  echo "Backing up $prompt..."
  promptpilot save $prompt -m "Automated backup $(date)"
done

echo "All prompts backed up!"
```
