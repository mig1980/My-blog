# Azure OpenAI Setup Guide

## Configuration Changes

The portfolio automation has been migrated from GitHub Models to Azure OpenAI for better reliability and no rate limits.

### Environment Variable

Set your Azure OpenAI API key:

```bash
# Windows PowerShell
$env:AZURE_OPENAI_API_KEY="your-azure-openai-api-key"

# Linux/Mac
export AZURE_OPENAI_API_KEY="your-azure-openai-api-key"
```

### Azure OpenAI Configuration

- **Endpoint**: `https://myportfolious2-resource.cognitiveservices.azure.com/openai/`
- **Deployment**: `gpt-5.1-chat`
- **API Version**: `2024-05-01-preview`
- **Note**: GPT-5.1-chat requires `max_completion_tokens` parameter instead of `max_tokens`

### Installation

Update dependencies:

```bash
pip install -r scripts/requirements.txt
```

### Usage

Run automation with default settings (uses gpt-5.1-chat deployment):

```bash
python scripts/portfolio_automation.py --data-source ai
```

Use a different deployment:

```bash
python scripts/portfolio_automation.py --model gpt-4o --data-source ai
```

### GitHub Actions

Update your GitHub Actions secrets:

1. Go to repository Settings → Secrets and variables → Actions
2. Add new secret: `AZURE_OPENAI_API_KEY`
3. Update workflow file to use new secret instead of `GH_TOKEN`

### Benefits

- ✅ **Higher rate limits**: No more HTTP 429 errors
- ⚠️ **Temperature control**: GPT-5.1 only supports default temperature (1.0)
- ✅ **Larger context**: Support for longer prompts and responses
- ✅ **Better reliability**: Enterprise-grade Azure infrastructure
- ✅ **Cost control**: Pay-per-use with predictable pricing

### Troubleshooting

If you get authentication errors:
- Verify `AZURE_OPENAI_API_KEY` is set correctly
- Check that your Azure OpenAI resource is active
- Ensure the deployment name matches (`gpt-5.1-chat`)

If you get endpoint errors:
- Verify the endpoint URL matches your Azure resource
- Check that the API version is supported by your deployment
