# GitHub Secrets Setup for Hands-Off Pi Deployment

## Quick Start

Your Pi will auto-connect to your hotspot on boot using credentials stored as GitHub Secrets. No keyboards or monitors needed.

## Step 1: Create SSH Key for GitHub Actions

```bash
ssh-keygen -t ed25519 -f ~/.ssh/divinofax_pi -C "divinofax-github"
# Press Enter to skip passphrase

# Add to Pi's authorized_keys
ssh-copy-id -i ~/.ssh/divinofax_pi.pub oracle@10.0.0.95

# Get the private key for GitHub
cat ~/.ssh/divinofax_pi
```

## Step 2: Add GitHub Secrets

Go to: **GitHub Repo → Settings → Secrets and variables → Actions → New repository secret**

Add these secrets:

| Secret | Value |
|--------|-------|
| `PI_HOST` | `10.0.0.95` |
| `PI_USER` | `oracle` |
| `PI_SSH_KEY` | *(paste entire private key from above)* |
| `HOTSPOT_SSID` | Your phone hotspot name |
| `HOTSPOT_PASSWORD` | Your hotspot password |
| `CLAUDE_API_KEY` | Your Claude API key |

## Step 3: Deploy

Push to `claude/zealous-poincare` branch or run workflow manually.

## Step 4: Access Pi

After Pi boots:
1. Connect your device to the same hotspot
2. Open `http://10.0.0.95:5000` in browser
3. Use dashboard to connect to local WiFi

Done!
