# 📱 iOS Shortcut for DivinoFax Dashboard

Control your dashboard from iPhone or iPad using iOS Shortcuts.

## Installation

### Method 1: Using Direct URL (Easiest)

1. **Open Shortcuts app** on your iPhone/iPad
2. **Create New Shortcut**
3. **Paste each shortcut below**

---

## Shortcut 1: Check Dashboard Status

```
1. Add "Get contents of URL"
   URL: http://divinofax.local:5000/api/status

2. Add "Ask for [Number/Text]"
   Question: "Dashboard Status"

3. Set it to display the response
```

**Or use this simpler version:**

1. Add action: "Open URL"
2. Set URL to: `http://divinofax.local:5000`
3. Name it: "📊 Open Dashboard"

---

## Shortcut 2: Dashboard Status Check

```
Shortcut Name: "🔮 DivinoFax Status"

1. Open URL
   - http://10.0.0.95:5000/api/status

2. Get Dictionary Value
   - running (shows true/false)

3. Show Result Alert
   - If running = true: Show "🟢 Dashboard is Running"
   - If running = false: Show "🔴 Dashboard is Stopped"
```

---

## Shortcut 3: Quick Open Dashboard

```
Shortcut Name: "📲 Open DivinoFax"

1. Open URL
   - http://divinofax.local:5000

2. Wait 1 second
```

**Add to Home Screen:**
- Name: "🔮 DivinoFax"
- Icon: Choose an oracle/crystal icon
- Full Screen: Off

---

## Shortcut 4: Control System (Requires SSH)

For full control (start/stop/restart), you need SSH access. Here's a setup:

### Install Termius or SSH App
- App: "Termius" or "Prompt 3"
- Add connection: `oracle@divinofax.local`
- Use SSH key (already configured on Pi)

### Quick Commands in Shortcut:
Create shortcuts that run SSH commands:

```
Shortcut: "▶️ Start DivinoFax"
1. Get SSH Connection (Termius/Prompt)
2. Execute command:
   sudo systemctl start divinofax
3. Show "✅ DivinoFax started"
```

---

## Simpler Alternative: Using Automations

### Create an iOS Automation

1. **Shortcuts app → Automations**
2. **Create new automation**
3. **Set trigger:**
   - Time of day (e.g., 9:00 AM for art events)
   - Or: When arriving at location

4. **Add action:**
   - Open URL: `http://divinofax.local:5000`

---

## Even Simpler: Just Use Safari

If shortcuts feel complex, just use Safari:

1. **Bookmark this:**
   ```
   http://divinofax.local:5000
   ```

2. **Add to home screen:**
   - Open in Safari
   - Tap Share → Add to Home Screen
   - Name: "🔮 DivinoFax Dashboard"

Now you have a one-tap access from your phone!

---

## Testing from iPhone

**Before trying shortcuts, test manually:**

1. Open Safari on iPhone
2. Go to: `http://divinofax.local:5000`
3. Should load the dashboard

If it doesn't work:
- Try IP address: `http://10.0.0.95:5000`
- Make sure iPhone is on same WiFi as Pi
- Restart iPhone WiFi

---

## Recommended Setup

**Easiest method for casual use:**

1. ✅ **Safari Bookmark** → Quick access
2. ✅ **Home Screen Shortcut** → One-tap open
3. ✅ **Termius SSH App** → For full control if needed

**Best method for art events:**

1. ✅ **Termius SSH app** → Full control (start/stop/restart)
2. ✅ **Home Screen Bookmark** → Quick status check
3. ✅ **Automation** → Auto-start at event time

---

## URLs You'll Need

| Action | URL |
|--------|-----|
| Open Dashboard | `http://divinofax.local:5000` |
| API Status | `http://divinofax.local:5000/api/status` |
| Backup IP | `http://10.0.0.95:5000` |

---

## Troubleshooting

### "Cannot connect"
- Check if on same WiFi as Pi
- Restart Pi
- Restart iPhone WiFi
- Try IP address instead: `10.0.0.95:5000`

### "divinofax.local not found"
- Your iPhone doesn't have mDNS
- Use IP address: `http://10.0.0.95:5000` instead

### For full control (start/stop)
- Install **Termius** app
- Add SSH connection to Pi
- Run: `sudo systemctl restart divinofax`

---

## Quick Setup Summary

**3 minutes to iOS control:**

1. ✅ Install Termius app (free)
2. ✅ Add Host: `divinofax.local`, User: `oracle`
3. ✅ Create Safari bookmark to `http://10.0.0.95:5000`
4. ✅ Add bookmark to home screen
5. ✅ Done!

**Now you can:**
- 📲 Tap to open dashboard
- 🔧 Use Termius for SSH control if needed
- 📊 Monitor from anywhere on your home WiFi
