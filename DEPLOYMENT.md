# Claude API Deployment to Raspberry Pi

## Overview

Two deployment methods are available:

1. **GitHub Actions** (Recommended) - Automatic deployment when you push code
2. **Manual Script** - Direct SSH deployment with `deploy_claude_api.sh`

Both use your `CLAUDE_API_KEY` secret securely and handle environment setup automatically.

---

## Method 1: GitHub Actions Deployment (Recommended)

### Prerequisites

✅ You have `CLAUDE_API_KEY` in GitHub Secrets (already done)
✅ Pi has internet access and can be reached via SSH
✅ Your SSH key is authorized on Pi (or password auth enabled)

### How It Works

Every time you push code to `main` or `claude/zealous-poincare`:
1. Workflow automatically triggers
2. Code is deployed to Pi using rsync
3. Environment variables are configured
4. Service is restarted
5. Health checks verify deployment

### Workflow Triggers

The workflow automatically runs when you push changes to:
- `.github/workflows/deploy-claude-api.yml` (workflow itself)
- `src/**` (Python code)
- `config/**` (configuration)
- `web_dashboard.py` (dashboard)
- `templates/**` (UI)
- `test_claude_integration.py` (tests)

### To Deploy

**Option A: Push code to GitHub**
```bash
git push origin claude/zealous-poincare
```

The workflow will automatically:
1. Check out the code
2. Verify `CLAUDE_API_KEY` secret exists
3. Deploy to Pi
4. Test the integration
5. Restart the service

**Option B: Trigger workflow manually**
1. Go to: https://github.com/YOUR-USERNAME/YOUR-REPO
2. Click **Actions** tab
3. Click **Deploy Claude API to Pi** workflow
4. Click **Run workflow** button
5. Select your branch
6. Watch the deployment in real-time

### Monitor Deployment

1. Go to **Actions** tab on GitHub
2. Click the workflow run to see live output
3. Each step shows status: ✓ passed, ✗ failed

### If Deployment Fails

Check the workflow logs:
1. Click on the failed run
2. Expand the failed step
3. Look for error messages
4. Common issues:
   - **SSH connection failed**: Pi offline or IP changed
   - **Secret not found**: Verify `CLAUDE_API_KEY` exists in GitHub Secrets
   - **Code conflicts**: Merge conflicts in deployment

---

## Method 2: Manual Deployment Script

### Prerequisites

✅ Your laptop can SSH to Pi: `ssh oracle@10.0.0.95`
✅ `CLAUDE_API_KEY` environment variable is set
✅ `rsync` is installed (comes with most Linux/macOS)

### Setup

1. **Get your API key from GitHub Secrets** (don't commit it locally)
2. **Set environment variable**:
   ```bash
   export CLAUDE_API_KEY="sk-ant-v1-your-actual-key"
   ```

3. **Verify it's set**:
   ```bash
   echo $CLAUDE_API_KEY
   # Should output: sk-ant-v1-...
   ```

### Deploy

From the repository root:

```bash
cd /path/to/divinofax/.claude/worktrees/zealous-poincare

# Make script executable
chmod +x deploy_claude_api.sh

# Run deployment
./deploy_claude_api.sh
```

### What It Does

1. ✓ Checks `CLAUDE_API_KEY` is set
2. ✓ Verifies Pi is reachable
3. ✓ Syncs code to Pi (skips .git, models, logs)
4. ✓ Adds API key to Pi's `~/.bashrc`
5. ✓ Tests Claude API integration
6. ✓ Restarts the DivinoFax service
7. ✓ Verifies deployment succeeded

### Output Example

```
🚀 Divinofax Claude API Deployment
====================================

Target: oracle@10.0.0.95:/home/oracle/divinofax
Local: /Users/kathrynbennett/divinofax

✓ API key detected: sk-ant-v1-xxxx...
✓ Pi is accessible

📤 Deploying code to Pi...
✓ Code deployed

⚙️  Setting up environment variables...
✓ Environment variables configured

🧪 Testing Claude API integration...
Running haiku generation test...
✓ Generated valid haiku: ...

✅ Deployment Complete!

📡 Access the dashboard:
   http://10.0.0.95:5000

⚙️  Configuration sections available:
   • 📡 WiFi Connection - Connect to networks
   • 🤖 Claude API Setup - Validate/manage API key
```

---

## Post-Deployment Verification

### 1. Access Dashboard

Open in browser: **http://10.0.0.95:5000**

You should see:
- System status (running/stopped)
- Recent fortunes
- **⚙️ Configuration** section at bottom

### 2. Verify Claude API

Scroll to **🤖 Claude API Setup**:
- Status badge should show **✓ Configured**
- API key field should show `sk-ant-v1-... (already set)`

### 3. Test WiFi (Optional)

Scroll to **📡 WiFi Connection**:
- Should show current connection status
- Can scan and connect to new networks
- See available WiFi networks list

### 4. Run Integration Test on Pi

```bash
ssh oracle@10.0.0.95

cd /home/oracle/divinofax

# The API key should be in environment from ~/.bashrc
python3 test_claude_integration.py
```

Expected output:
```
=== Divinofax Claude API Integration Test ===

✓ Configuration loaded
  - Using Claude API: True
  - Model: claude-3-5-sonnet-20241022
  - API Key: sk-ant-v1-...

✓ LLM Engine initialized

=== Generating test haikus with context ===

Test 1: Transformation
⏱️  Generation time: 8.23s
✓ Generated haiku:
[haiku text]

...

✅ All tests passed! Claude API integration is working.
```

### 5. Monitor Logs

Real-time log monitoring:
```bash
ssh oracle@10.0.0.95
tail -f /home/oracle/divinofax/divinofax.log | grep -i "haiku\|claude\|api"
```

---

## Troubleshooting

### "CLAUDE_API_KEY not set"

**Problem**: Environment variable isn't configured

**Solution**:
```bash
# Check if set
echo $CLAUDE_API_KEY

# If empty, set it
export CLAUDE_API_KEY="sk-ant-v1-your-key"

# Make permanent on Pi
ssh oracle@10.0.0.95 'echo "export CLAUDE_API_KEY=\"sk-...\"" >> ~/.bashrc'
```

### "Cannot connect to Pi"

**Problem**: SSH connection fails

**Solution**:
```bash
# Verify Pi is reachable
ping 10.0.0.95

# Check SSH access
ssh -v oracle@10.0.0.95 "echo ok"

# If using password auth (no SSH key)
ssh -o PreferredAuthentications=password oracle@10.0.0.95
```

### "Invalid Claude API key format"

**Problem**: Key doesn't start with `sk-ant-v1-`

**Solution**:
1. Go to https://console.anthropic.com/api_keys
2. Create a new API key
3. Copy the entire key (no spaces, no quotes)
4. Update in GitHub Secrets OR re-export environment variable

### "Deployment succeeded but API shows as not configured"

**Problem**: API key isn't being loaded on Pi

**Solution**:
```bash
# On Pi, verify environment variable is set
ssh oracle@10.0.0.95
echo $CLAUDE_API_KEY

# If empty, manually export it
export CLAUDE_API_KEY="sk-ant-v1-your-key"

# Then test
python3 /home/oracle/divinofax/test_claude_integration.py
```

### "Test timeout after 60 seconds"

**Problem**: anthropic library not installed or network issue

**Solution**:
```bash
# On Pi, install anthropic library
pip3 install --user anthropic

# Try test again
python3 test_claude_integration.py
```

### Dashboard shows "Error loading status"

**Problem**: API endpoints not responding

**Solution**:
```bash
# Restart the dashboard service
ssh oracle@10.0.0.95
sudo systemctl restart divinofax

# Or restart manually
cd /home/oracle/divinofax
python3 web_dashboard.py
```

---

## Performance After Deployment

### Expected Performance

| Metric | Value |
|--------|-------|
| Haiku generation time | 5-15 seconds |
| API latency | 3-5 seconds |
| Dashboard response | <1 second |
| WiFi connection time | 10-30 seconds |

### Monitoring

**Dashboard Status**:
- http://10.0.0.95:5000 - Check system status
- Recent fortunes show generation times

**API Costs**:
- https://console.anthropic.com/account/usage
- ~$0.01 per haiku
- Monitor daily/monthly spend

**System Resources**:
```bash
ssh oracle@10.0.0.95
free -h          # Memory usage
df -h            # Disk space
top -b -n 1      # CPU usage
```

---

## Rollback

If something goes wrong after deployment:

### Revert to Previous Version

```bash
# On your laptop
git revert HEAD
git push origin claude/zealous-poincare
# Workflow will auto-deploy previous version

# OR manually
git reset --hard HEAD~1
bash deploy_claude_api.sh
```

### Disable Claude API Temporarily

Edit on Pi:
```bash
ssh oracle@10.0.0.95

# Edit config
nano /home/oracle/divinofax/config/divinofax.yaml

# Change line 65 to:
# use_claude_api: false

# Save (Ctrl+O, Enter, Ctrl+X)

# Restart
sudo systemctl restart divinofax
```

---

## Next Steps

1. ✅ Deploy using **GitHub Actions** or **manual script**
2. ✅ Access dashboard at http://10.0.0.95:5000
3. ✅ Verify Claude API is configured
4. ✅ Test haiku generation with RFID card
5. ✅ Monitor costs at console.anthropic.com
6. ✅ Check logs with: `tail -f /home/oracle/divinofax/divinofax.log`

---

## Support

If you encounter issues:

1. Check **Troubleshooting** section above
2. Review **GitHub Actions** logs for detailed error messages
3. Run **Integration test** to verify API connection
4. Check **Pi logs** with: `ssh oracle@10.0.0.95 tail -f /home/oracle/divinofax/divinofax.log`

For GitHub Actions issues specifically, see `.github/workflows/deploy-claude-api.yml`
