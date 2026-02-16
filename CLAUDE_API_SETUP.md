# Claude API Integration Setup Guide

## What Changed

Divinofax now uses **Claude API for haiku generation** instead of running slow local Llama models. This gives you:

- ⚡ **5-15 second haikus** (vs 60-180 seconds with local Llama)
- 🎯 **Higher quality** output from Claude's superior language understanding
- 🌙 **All celestial context preserved** - moon phases, zodiac, oracle cards all included
- 📱 **Works anywhere** with internet access on Pi

## Quick Start

### Step 1: Get a Claude API Key

1. Go to [console.anthropic.com](https://console.anthropic.com)
2. Sign up or log in
3. Go to "API Keys" section
4. Create a new API key
5. Copy your key (format: `sk-ant-v1-...`)

### Step 2: Set Environment Variable on Pi

SSH into your Raspberry Pi and set the API key:

```bash
export CLAUDE_API_KEY="sk-ant-v1-your-actual-key-here"
```

For permanent storage, add to `~/.bashrc`:

```bash
echo 'export CLAUDE_API_KEY="sk-ant-v1-your-actual-key-here"' >> ~/.bashrc
source ~/.bashrc
```

### Step 3: Use Dashboard to Configure (Recommended)

1. Open the Divinofax dashboard in your browser (http://pi-ip:5000)
2. Click "Settings" (or navigate to the config section)
3. Enter your Claude API key
4. Click "Enable Claude API"
5. Test haiku generation

### Step 4: Verify It Works

```bash
python3 test_claude_integration.py
```

You should see successful haiku generations with timing information.

## GitHub Secrets (Secure Deployment)

If using GitHub Actions to deploy to Pi:

1. Go to your GitHub repo → Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Name: `CLAUDE_API_KEY`
4. Value: `sk-ant-v1-your-actual-key`
5. In your deployment workflow, use: `export CLAUDE_API_KEY=${{ secrets.CLAUDE_API_KEY }}`

## Configuration Files

### Local Configuration (`config/divinofax.yaml`)

```yaml
llm:
  use_claude_api: true  # Enable Claude API
  claude_api_key: ${CLAUDE_API_KEY}  # Load from environment variable
  claude_model: claude-3-5-sonnet-20241022
  claude_temperature: 0.8
  claude_max_tokens: 150
```

The `${CLAUDE_API_KEY}` placeholder is replaced at runtime with the actual key from your environment variable.

### Environment Variable

The API key is loaded from `CLAUDE_API_KEY` environment variable, not stored in config files.

## Dashboard Configuration Endpoints

New REST endpoints are available:

### WiFi Configuration
- `GET /api/config/wifi/status` - Current WiFi connection status
- `GET /api/config/wifi/networks` - Scan available WiFi networks
- `POST /api/config/wifi/connect` - Connect to a WiFi network
  ```json
  {"ssid": "YourNetwork", "password": "YourPassword"}
  ```

### LLM Configuration
- `GET /api/config/llm` - Get current LLM config (API key masked)
- `POST /api/config/llm` - Save Claude API key
  ```json
  {"api_key": "sk-ant-v1-...", "use_claude_api": true}
  ```
- `POST /api/config/llm/validate` - Validate API key format
  ```json
  {"api_key": "sk-ant-v1-..."}
  ```

## Fallback Behavior

If Claude API is not configured or fails:
1. System automatically falls back to local Llama model (slow)
2. Or falls back to mock engine with sample haikus
3. Check logs for error messages

## Cost

Claude API usage costs money. Typical costs:
- **~$0.008-0.015 per haiku** depending on prompt length
- A 50-haiku event would cost ~$0.40-0.75
- No charge for API failures or errors

## Troubleshooting

### "Claude API key not configured"
- Verify `export CLAUDE_API_KEY="sk-..."` is set
- Check: `echo $CLAUDE_API_KEY`

### "Invalid Claude API key format"
- Keys must start with `sk-`
- Verify you copied the full key without spaces

### "Connection timeout"
- Check Pi has internet access
- Test: `ping api.anthropic.com`
- Check your network isn't blocking API calls

### Slow generation (> 20 seconds)
- Network latency issue
- Claude API is busy (unlikely)
- Check Pi network speed: `speedtest-cli`

## Prompt Quality

The existing prompt system is fully preserved and enhanced:

**Included in every haiku generation:**
- Oracle card title and description
- Card suit and tone (Signal, Circuit, Archive, Glitch, Sync)
- Moon phase context ("under the full moon", "during the waning crescent", etc.)
- Zodiac/astrological influence for current date
- Guidance to create poetic, mystical output
- Examples of different poetic forms (haiku, couplet, tercet, free verse)

Claude uses all this context to generate high-quality, personalized haikus that feel like authentic oracle guidance.

## Next Steps

1. Set `CLAUDE_API_KEY` environment variable
2. Restart the Divinofax service or reload config
3. Test haiku generation via dashboard or RFID card
4. Monitor costs via [Anthropic console](https://console.anthropic.com/account/usage)

Questions? Check the main README.md or review the implementation in `src/llm_engine.py`.
