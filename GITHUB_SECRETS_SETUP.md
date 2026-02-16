# GitHub Secrets Setup Guide

## What Are GitHub Secrets?

GitHub Secrets allow you to store sensitive information (like API keys) securely without committing them to your repository. This keeps your API key safe while allowing automated deployments to access it.

## Step-by-Step Setup

### Step 1: Go to Your GitHub Repository Settings

1. Open your GitHub repository in a browser
2. Click on **Settings** (top menu bar)
3. In the left sidebar, click **Secrets and variables** → **Actions**

You should see a screen like this:
```
Repository secrets
No secrets found - Create your first secret
```

### Step 2: Create a New Secret

1. Click the green button **"New repository secret"**
2. You'll see a form with two fields:
   - **Name**: `CLAUDE_API_KEY`
   - **Secret**: [Your actual API key]

### Step 3: Enter Your Claude API Key

1. Get your API key from [console.anthropic.com/api_keys](https://console.anthropic.com/api_keys)
   - It looks like: `sk-ant-v1-xxxxxxxxxxxx...`
2. Copy the entire key
3. Paste it into the **Secret** field
4. **DO NOT** include quotes or extra spaces
5. Click **"Add secret"**

GitHub will now display:
```
✓ CLAUDE_API_KEY
Updated just now
```

## Using the Secret in Your Deployment

### For Manual Pi Deployment

When deploying to your Pi, export the secret as an environment variable:

```bash
# On your local machine, before SSH-ing to Pi
export CLAUDE_API_KEY="sk-ant-v1-your-actual-key"

# Then SSH to Pi
ssh oracle@10.0.0.95

# Set it on Pi
export CLAUDE_API_KEY="sk-ant-v1-your-actual-key"

# Or add to ~/.bashrc for persistence
echo 'export CLAUDE_API_KEY="sk-ant-v1-your-actual-key"' >> ~/.bashrc
source ~/.bashrc
```

### For GitHub Actions Deployment

If you have a GitHub Actions workflow file (`.github/workflows/deploy.yml`), reference the secret:

```yaml
name: Deploy to Pi

on: [push]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Deploy to Raspberry Pi
        env:
          CLAUDE_API_KEY: ${{ secrets.CLAUDE_API_KEY }}
        run: |
          # Your deployment script here
          ssh oracle@10.0.0.95 "export CLAUDE_API_KEY=$CLAUDE_API_KEY && cd /home/oracle/divinofax && ./deploy.sh"
```

The `${{ secrets.CLAUDE_API_KEY }}` syntax safely injects your secret into the workflow without logging it.

## Security Best Practices

### ✅ DO:
- Store the full API key in GitHub Secrets
- Reference it as `${{ secrets.CLAUDE_API_KEY }}` in workflows
- Use environment variables on Pi (`export CLAUDE_API_KEY=...`)
- Rotate your key periodically in Anthropic console
- Delete old keys you're no longer using

### ❌ DON'T:
- Commit API keys to the repository
- Log or print the API key anywhere
- Share the key in Slack/email/Discord
- Leave the key hardcoded in config files
- Use the same key across multiple projects

## Checking If It Works

### Test 1: Verify Secret is Set

On your Pi, run:
```bash
echo $CLAUDE_API_KEY
```

You should see: `sk-ant-v1-...` (not empty)

### Test 2: Test API Connection

Run the integration test:
```bash
cd /home/oracle/divinofax
python3 test_claude_integration.py
```

You should see successful haiku generations.

### Test 3: Check Dashboard

1. Open http://pi-ip:5000
2. Scroll to "⚙️ Configuration" section
3. Under "🤖 Claude API Setup":
   - Status should show "✓ Configured"
   - You can validate the key with the "✓ Validate Key" button

## Troubleshooting

### "Claude API key not configured"
**Problem**: The environment variable is not set
**Solution**:
```bash
# Check if it's set
echo $CLAUDE_API_KEY

# If empty, set it
export CLAUDE_API_KEY="sk-ant-v1-..."

# Make it permanent
echo 'export CLAUDE_API_KEY="sk-ant-v1-..."' >> ~/.bashrc
source ~/.bashrc
```

### "Invalid API key format"
**Problem**: Key doesn't start with `sk-`
**Solution**:
1. Go to [console.anthropic.com/api_keys](https://console.anthropic.com/api_keys)
2. Double-check you copied the entire key
3. Keys must start with `sk-ant-v1-`

### "Invalid Claude API key"
**Problem**: The key is invalid or expired
**Solution**:
1. Delete the old secret in GitHub Settings
2. Create a new API key in Anthropic console
3. Add it as a new secret in GitHub

### Secret Not Available in Workflow
**Problem**: GitHub Action can't access the secret
**Solution**: Make sure:
1. Secret is named exactly `CLAUDE_API_KEY`
2. You're using `${{ secrets.CLAUDE_API_KEY }}` syntax
3. The workflow job has `permissions: read-all` (some setups need this)

## Changing Your API Key

If you need to update the key:

1. **Create a new key** in [Anthropic console](https://console.anthropic.com/api_keys)
2. **Delete the old secret** in GitHub Settings
3. **Create a new secret** with the same name `CLAUDE_API_KEY`
4. **Restart your Pi service** or re-export the environment variable

## Cost Monitoring

Once your API key is working, monitor costs:

1. Go to [console.anthropic.com/account/usage](https://console.anthropic.com/account/usage)
2. You'll see:
   - Daily/monthly usage
   - Cost per haiku (~$0.01)
   - Total spend

## Environment Variable Config File

Your `config/divinofax.yaml` contains:

```yaml
llm:
  use_claude_api: true
  claude_api_key: ${CLAUDE_API_KEY}  # This gets replaced at runtime
  claude_model: claude-3-5-sonnet-20241022
```

The `${CLAUDE_API_KEY}` placeholder is replaced with the actual value from your environment variable when the config loads.

**Important**: The config file NEVER contains your actual key—only the placeholder.

## FAQ

**Q: Can someone steal my API key from GitHub?**
A: No. GitHub Secrets are encrypted and not visible in:
- Public repositories
- Workflow logs
- Pull requests
- Forked repositories (they don't inherit parent secrets)

**Q: Can I use the same key across multiple servers?**
A: Yes, but not recommended. Best practice is one key per service/location.

**Q: What happens if my key gets compromised?**
A: Immediately:
1. Delete the key in Anthropic console (stops all requests)
2. Delete the GitHub Secret
3. Create a new API key
4. Add the new key to GitHub Secrets
5. Redeploy your Pi with `export CLAUDE_API_KEY=new-key`

**Q: Can I set the key without GitHub Secrets?**
A: Yes, you can set it manually on your Pi:
```bash
echo 'export CLAUDE_API_KEY="sk-..."' >> ~/.bashrc
```

But GitHub Secrets is more secure for automated deployments.

## Next Steps

1. ✅ Create GitHub secret `CLAUDE_API_KEY`
2. ✅ Deploy to Pi (the env var will be passed)
3. ✅ Test with `test_claude_integration.py`
4. ✅ Verify in dashboard at http://pi-ip:5000
5. ✅ Monitor costs at console.anthropic.com

Questions? Check `CLAUDE_API_SETUP.md` for more details on configuration.
