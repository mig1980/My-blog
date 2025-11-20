# Running Portfolio Automation with Azure AI Foundry

This guide explains how to set up and run the portfolio automation script using Azure AI Foundry (formerly Azure OpenAI Service).

## Prerequisites

- Azure subscription with access to Azure AI Foundry
- Python 3.11 or higher
- Git (for cloning the repository)

## Step 1: Create Azure AI Foundry Resource

### Option A: Using Azure Portal

1. Go to [Azure Portal](https://portal.azure.com)
2. Click **"Create a resource"**
3. Search for **"Azure OpenAI"** or **"Azure AI Services"**
4. Click **"Create"**
5. Fill in the details:
   - **Subscription**: Select your Azure subscription
   - **Resource Group**: Create new or use existing
   - **Region**: Choose a region (e.g., East US, West Europe)
   - **Name**: `MyPortfolio` (or your preferred name)
   - **Pricing Tier**: Standard S0
6. Click **"Review + Create"**, then **"Create"**

### Option B: Using Azure CLI

```bash
# Login to Azure
az login

# Create resource group
az group create --name MyPortfolioRG --location eastus

# Create Azure OpenAI resource
az cognitiveservices account create \
  --name MyPortfolio \
  --resource-group MyPortfolioRG \
  --kind OpenAI \
  --sku S0 \
  --location eastus
```

## Step 2: Deploy GPT-4 Model

### Using Azure Portal

1. Navigate to your Azure OpenAI resource
2. Click **"Go to Azure OpenAI Studio"**
3. In Azure OpenAI Studio:
   - Go to **"Deployments"** → **"Create new deployment"**
   - **Model**: Select `gpt-4` (or `gpt-4-turbo`, `gpt-4o`)
   - **Deployment name**: `gpt-4.1` (must match the code)
   - **Deployment type**: Standard
   - Click **"Create"**

### Using Azure CLI

```bash
# Deploy GPT-4 model
az cognitiveservices account deployment create \
  --name MyPortfolio \
  --resource-group MyPortfolioRG \
  --deployment-name gpt-4.1 \
  --model-name gpt-4 \
  --model-version "0613" \
  --model-format OpenAI \
  --sku-capacity 1 \
  --sku-name "Standard"
```

## Step 3: Get API Key and Endpoint

### Using Azure Portal

1. Navigate to your Azure OpenAI resource
2. Go to **"Keys and Endpoint"** (left menu)
3. Copy:
   - **KEY 1** (your API key)
   - **Endpoint** (should be like `https://MyPortfolio.openai.azure.com/`)

### Using Azure CLI

```bash
# Get API key
az cognitiveservices account keys list \
  --name MyPortfolio \
  --resource-group MyPortfolioRG

# Get endpoint
az cognitiveservices account show \
  --name MyPortfolio \
  --resource-group MyPortfolioRG \
  --query "properties.endpoint"
```

## Step 4: Configure the Automation Script

The script is already configured for Azure AI Foundry. Verify the endpoint matches your resource:

**File**: `scripts/portfolio_automation.py` (line 102-105)

```python
self.client = OpenAI(
    base_url="https://MyPortfolio.openai.azure.com/openai/v1/",
    api_key=self.azure_api_key
)
```

**If your resource has a different name**, update the `base_url`:
- Format: `https://<your-resource-name>.openai.azure.com/openai/v1/`
- Example: `https://my-custom-name.openai.azure.com/openai/v1/`

## Step 5: Set Environment Variables

### Windows (PowerShell)

```powershell
# Set Azure OpenAI API key
$env:AZURE_OPENAI_API_KEY="your-api-key-from-step-3"

# Set Alpha Vantage API key (for market data)
$env:ALPHAVANTAGE_API_KEY="your-alphavantage-key"

# Optional: Set other API keys
$env:FINNHUB_API_KEY="your-finnhub-key"
$env:PEXELS_API_KEY="your-pexels-key"
$env:PIXABAY_API_KEY="your-pixabay-key"
```

### Linux/Mac (Bash)

```bash
# Set Azure OpenAI API key
export AZURE_OPENAI_API_KEY="your-api-key-from-step-3"

# Set Alpha Vantage API key (for market data)
export ALPHAVANTAGE_API_KEY="your-alphavantage-key"

# Optional: Set other API keys
export FINNHUB_API_KEY="your-finnhub-key"
export PEXELS_API_KEY="your-pexels-key"
export PIXABAY_API_KEY="your-pixabay-key"
```

### Permanent Environment Variables (Windows)

```powershell
# Set permanently (requires restart of terminal)
[System.Environment]::SetEnvironmentVariable('AZURE_OPENAI_API_KEY', 'your-api-key', 'User')
[System.Environment]::SetEnvironmentVariable('ALPHAVANTAGE_API_KEY', 'your-av-key', 'User')
```

## Step 6: Install Dependencies

```bash
# Navigate to repository
cd path/to/My-blog

# Install Python dependencies
pip install -r scripts/requirements.txt
```

## Step 7: Run the Automation

### Basic Usage

```bash
# Run with Alpha Vantage data source (recommended)
python scripts/portfolio_automation.py --data-source alphavantage
```

### Advanced Options

```bash
# Specify week number manually
python scripts/portfolio_automation.py --data-source alphavantage --week 6

# Use a different deployment name
python scripts/portfolio_automation.py --data-source alphavantage --model gpt-4o

# Override evaluation date
python scripts/portfolio_automation.py --data-source alphavantage --eval-date 2025-11-15

# Use AI for data generation (requires Prompt A)
python scripts/portfolio_automation.py --data-source ai
```

## Step 8: GitHub Actions Setup (Optional)

To automate weekly runs using GitHub Actions:

1. Go to your GitHub repository
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Add the following secrets:
   - `AZURE_OPENAI_API_KEY`: Your Azure API key
   - `ALPHAVANTAGE_API_KEY`: Your Alpha Vantage key
   - `FINNHUB_API_KEY`: (Optional) Your Finnhub key
   - `PEXELS_API_KEY`: (Optional) For hero images
   - `PIXABAY_API_KEY`: (Optional) For hero images

The workflow is already configured in `.github/workflows/weekly-portfolio.yml`

### Trigger Manual Run

1. Go to **Actions** tab in GitHub
2. Select **"Weekly Portfolio Update"**
3. Click **"Run workflow"**
4. Fill in optional parameters (week number, eval date)
5. Click **"Run workflow"**

## Troubleshooting

### Error: "AI client not initialized"

**Cause**: `AZURE_OPENAI_API_KEY` environment variable not set

**Solution**:
```powershell
$env:AZURE_OPENAI_API_KEY="your-api-key"
```

### Error: "Model not found" or "Deployment not found"

**Cause**: Deployment name mismatch

**Solution**: Verify deployment name in Azure OpenAI Studio matches the `--model` parameter (default: `gpt-4.1`)

### Error: "Invalid endpoint"

**Cause**: Wrong endpoint URL in code

**Solution**: Update `base_url` in `portfolio_automation.py` line 103 to match your Azure resource name

### Error: "Rate limit exceeded"

**Cause**: Too many requests to Azure OpenAI

**Solution**: Azure OpenAI has higher limits than GitHub Models. Check your deployment quota in Azure Portal.

### Error: "Unauthorized" or "403 Forbidden"

**Cause**: Invalid API key or expired key

**Solution**: 
1. Regenerate API key in Azure Portal
2. Update environment variable
3. Verify key doesn't have extra spaces or quotes

## API Key Security

### Best Practices

1. **Never commit API keys** to Git
2. **Use environment variables** for local development
3. **Use GitHub Secrets** for CI/CD
4. **Rotate keys regularly** (every 90 days)
5. **Use separate keys** for development and production

### Rotate API Keys

```bash
# Regenerate key in Azure Portal
az cognitiveservices account keys regenerate \
  --name MyPortfolio \
  --resource-group MyPortfolioRG \
  --key-name key1

# Update environment variable with new key
$env:AZURE_OPENAI_API_KEY="new-api-key"
```

## Cost Estimation

### Azure OpenAI Pricing (as of 2025)

- **GPT-4 (8K context)**: ~$0.03 per 1K input tokens, ~$0.06 per 1K output tokens
- **GPT-4 Turbo (128K context)**: ~$0.01 per 1K input tokens, ~$0.03 per 1K output tokens
- **GPT-4o**: ~$0.005 per 1K input tokens, ~$0.015 per 1K output tokens

### Weekly Run Cost Estimate

Each weekly automation run:
- **Prompt B (Narrative)**: ~2,500 tokens input + ~1,500 tokens output = ~$0.18
- **Prompt C (Visuals)**: ~2,000 tokens input + ~1,000 tokens output = ~$0.15
- **Prompt D (HTML)**: ~1,000 tokens input + ~3,000 tokens output = ~$0.21

**Total per week**: ~$0.54 (using GPT-4)  
**Total per month**: ~$2.16 (4 weeks)  
**Total per year**: ~$28

*Note: Using `gpt-4o` can reduce costs by ~70%*

## Additional Resources

- [Azure OpenAI Service Documentation](https://learn.microsoft.com/en-us/azure/ai-services/openai/)
- [Azure OpenAI Studio](https://oai.azure.com/)
- [OpenAI Python Library](https://github.com/openai/openai-python)
- [Alpha Vantage API Documentation](https://www.alphavantage.co/documentation/)

## Support

For issues specific to:
- **Azure AI Foundry**: [Azure Support](https://azure.microsoft.com/en-us/support/)
- **Portfolio Automation**: Open an issue in this repository
- **API Keys**: Contact respective API providers

## Next Steps

1. ✅ Set up Azure AI Foundry resource
2. ✅ Deploy GPT-4 model
3. ✅ Configure environment variables
4. ✅ Run first automation
5. 🔄 Set up GitHub Actions for weekly automation
6. 📊 Monitor costs in Azure Portal
7. 🎨 Customize prompts in `Prompt/` directory
