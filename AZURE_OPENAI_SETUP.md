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

- **Endpoint**: `https://MyPortfolio.openai.azure.com/openai/v1/`
- **Deployment**: `gpt-4.1`
- **API Version**: `2024-05-01-preview`

### Installation

Update dependencies:

```bash
pip install -r scripts/requirements.txt
```

### Usage

Run automation with default settings (uses gpt-4.1 deployment):

```bash
python scripts/portfolio_automation.py --data-source alphavantage
```

Use a different deployment:

```bash
python scripts/portfolio_automation.py --model gpt-4o --data-source alphavantage
```

### GitHub Actions

Update your GitHub Actions secrets:

1. Go to repository Settings → Secrets and variables → Actions
2. Add new secret: `AZURE_OPENAI_API_KEY`
3. Update workflow file to use new secret instead of `GH_TOKEN`

### Benefits

- ✅ **Higher rate limits**: No more HTTP 429 errors
- ✅ **Temperature control**: Full support for 0.0 to 2.0
- ✅ **Larger context**: Support for longer prompts and responses
- ✅ **Better reliability**: Enterprise-grade Azure infrastructure
- ✅ **Cost control**: Pay-per-use with predictable pricing

### Troubleshooting

If you get authentication errors:
- Verify `AZURE_OPENAI_API_KEY` is set correctly
- Check that your Azure OpenAI resource is active
- Ensure the deployment name matches (`gpt-4.1`)

If you get endpoint errors:
- Verify the endpoint URL matches your Azure resource
- Check that the API version is supported by your deployment
