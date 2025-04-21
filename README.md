# PromptPilot

A fast, lightweight Python library and CLI tool for versioning, testing, and optimizing your AI prompts across multiple providers.

[![PyPI version](https://img.shields.io/pypi/v/promptpilot-cli.svg)](https://pypi.org/project/promptpilot-cli/)
[![Python versions](https://img.shields.io/pypi/pyversions/promptpilot-cli.svg)](https://pypi.org/project/promptpilot-cli/)
[![License](https://img.shields.io/github/license/doganarif/promptpilot.svg)](https://github.com/doganarif/promptpilot/blob/main/LICENSE)

## 🚀 Quick Start

```bash
# Install from PyPI
pip install promptpilot-cli

# Initialize a new prompt
promptpilot init my-summary --description "Summarize text in 3 paragraphs"

# Run an A/B test
promptpilot abtest my-summary --input sample.txt --provider openai
```

## ✨ Features

- **Version control** for your AI prompts, with or without Git
- **A/B testing** to compare prompts based on token usage and response quality
- **Multi-provider support** for OpenAI, Claude, Llama, and HuggingFace
- **Fast startup time** with lazy loading of dependencies
- **Live progress feedback** during operations
- **Extensible architecture** for custom providers and formatters
- **Python API** for integration into your own workflows

## 📋 Requirements

- Python 3.11+
- API keys for the services you want to use

## 🔧 Installation

```bash
pip install promptpilot-cli
```

For development:

```bash
git clone https://github.com/doganarif/promptpilot.git
cd promptpilot
pip install -e .
```

## ⚙️ Configuration

Create a `.env` file in your project root with your API keys:

```ini
# Required API keys (for the providers you use)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
LLAMA_API_KEY=llm-...

# Optional default models
PROMPTCTL_DEFAULT_MODEL=gpt-4o
PROMPTCTL_CLAUDE_MODEL=claude-3-opus-20240229
PROMPTCTL_LLAMA_MODEL=llama-3-70b-instruct

# Optional API URL for Llama
LLAMA_API_URL=https://api.llama-api.com
```

PromptPilot will automatically detect and use this file.

## 📖 CLI Usage Examples

### Initialize a new prompt

```bash
promptpilot init text-extractor \
  --description "Extract key information from documents" \
  --author "Jane Smith"
```

This creates `prompts/text-extractor.yml` with a template and metadata.

### Version Management

```bash
# Save current prompt state as a new version
promptpilot save summary -m "Added more detailed instructions"

# Show difference between versions
promptpilot diff summary

# List all versions of a prompt
promptpilot list summary

# List all available prompts
promptpilot list
```

### Run an A/B test

```bash
# Basic A/B test with OpenAI
promptpilot abtest summary --input article.txt --provider openai

# Testing with Claude
promptpilot abtest summary --input article.txt --provider claude --model claude-3-sonnet

# Include full responses in the output
promptpilot abtest summary --input article.txt --include-responses

# Output results in JSON format
promptpilot abtest summary --input article.txt --format json > results.json
```

## 💻 Python API Examples

### Basic A/B Testing

```python
from promptpilot.utils import load_prompt_versions
from promptpilot.models import Prompt
from promptpilot.providers import get_provider
from promptpilot.runner import ABTestRunner

# Load two prompt versions
prev, curr = load_prompt_versions("summary")

# Create prompt objects
prompt_a = Prompt(name="summary_v1", template=prev, version=1)
prompt_b = Prompt(name="summary_v2", template=curr, version=2)

# Initialize provider (OpenAI by default)
provider = get_provider("openai", model="gpt-4o")

# Run the A/B test
runner = ABTestRunner(provider)
input_text = open("article.txt").read()

result = runner.run_test(
    prompt_a=prompt_a,
    prompt_b=prompt_b,
    variables={"text": input_text},
    include_responses=True
)

# Display results
runner.display_results(result)

# Get the winner
winner_name, token_count = runner.get_winner(result)
print(f"Winner: {winner_name} with {token_count} tokens")
```

### Testing Multiple Prompt Variations

```python
from promptpilot.models import Prompt
from promptpilot.providers import get_provider
from promptpilot.runner import MultiPromptTestRunner

# Create multiple prompt variants
prompts = [
    Prompt(name="concise", 
           template="Summarize this text briefly:\n\n{text}", 
           version=1),
    Prompt(name="detailed", 
           template="Provide a comprehensive summary of the following text:\n\n{text}", 
           version=2),
    Prompt(name="bullet_points", 
           template="Extract the key points from this text as bullet points:\n\n{text}", 
           version=3)
]

# Initialize provider
provider = get_provider("claude", model="claude-3-opus-20240229")

# Test all prompts with the same input
runner = MultiPromptTestRunner(provider)
input_text = open("research_paper.txt").read()

result = runner.run_test(
    prompts=prompts,
    variables={"text": input_text}
)

# Display results
runner.display_results(result)

# Get prompts ranked by efficiency
ranked_prompts = runner.get_ranked_prompts(result)
print("Prompts ranked by token efficiency:", ranked_prompts)
```

### Batch Testing Across Multiple Inputs

```python
from promptpilot.models import Prompt, TestCase
from promptpilot.providers import get_provider
from promptpilot.runner import BatchTestRunner

# Create prompt variants
prompt_a = Prompt(name="generic", 
                  template="Summarize this text:\n\n{text}", 
                  version=1)
                  
prompt_b = Prompt(name="domain_specific", 
                  template="Summarize this scientific text for a general audience:\n\n{text}", 
                  version=2)

# Create test cases with different inputs
test_cases = [
    TestCase(
        name="news_article",
        variables={"text": open("news.txt").read()},
        description="General news article"
    ),
    TestCase(
        name="research_paper",
        variables={"text": open("research.txt").read()},
        description="Scientific research paper"
    ),
    TestCase(
        name="technical_doc",
        variables={"text": open("technical.txt").read()},
        description="Technical documentation"
    )
]

# Initialize provider
provider = get_provider("openai", model="gpt-4o")

# Run batch test
runner = BatchTestRunner(provider)
result = runner.run_batch_test(
    prompt_a=prompt_a,
    prompt_b=prompt_b,
    test_cases=test_cases
)

# Display results
runner.display_results(result)

# Get overall winner
overall_winner = runner.get_overall_winner(result)
print(f"Overall best prompt: {overall_winner.name}")

# Get best prompt for a specific case
best_for_research = runner.get_best_prompt_for_case(result, "research_paper")
print(f"Best prompt for research papers: {best_for_research}")
```

## 📁 Project Structure

```
my-project/
├── .env                 # API keys and config
├── prompts/             # Directory for prompt templates
│   ├── summary.yml      # Example prompt
│   ├── extractor.yml    # Another prompt
│   └── versions/        # Version history
│       └── summary/     # Directory for summary versions 
│           ├── v1_1714042811.yml
│           └── v2_1714042897.yml
├── inputs/              # Test inputs
│   ├── article.txt
│   └── paper.txt
└── scripts/             # Your Python scripts
    └── batch_test.py
```

## 🔍 Prompt File Format

Each prompt is stored as a YAML file:

```yaml
name: summary
description: Summarize text in three paragraphs
version: 2
author: Jane Smith
created: 2025-04-21
updated: 2025-04-21

prompt: |
  Create a concise summary of the following text. Focus on the main points
  and key details. Use about 3 paragraphs and make it engaging:
  
  {text}

variables:
  - name: text
    description: Input text for the prompt
    required: true

metadata:
  recommended_models: ["gpt-4o", "claude-3-opus"]
  token_estimate:
    input_multiplier: 1.0
    base_tokens: 50

history:
  - version: 1
    date: 2025-04-21
    prompt: |
      Summarize the following text in about 3 paragraphs:
      
      {text}
    message: "Initial version"
```

## 💡 Best Practices

- **Make small, incremental changes** between prompt versions to isolate effects
- **Use consistent test inputs** to ensure fair comparisons
- **Save versions regularly** using `promptpilot save` to track your improvements
- **Consider both token efficiency and output quality** in your evaluations
- **Use descriptive prompt and test case names** for better organization

## 🛠️ Troubleshooting

- **API Key Issues**: Ensure your `.env` file contains the correct API keys
- **Slow Startup**: Try updating to the latest version with `pip install -U promptpilot-cli`
- **Import Errors**: Install missing dependencies with `pip install 'promptpilot-cli[all]'`
- **Provider Not Found**: Check that you've specified a supported provider name
- **Version History Issues**: Use `promptpilot save` to explicitly save versions

## 📚 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📧 Contact

Arif Dogan - me@arif.sh

Project Link: [https://github.com/doganarif/promptpilot](https://github.com/doganarif/promptpilot)
