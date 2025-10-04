# Oracle Cards Setup Guide

This guide walks you through setting up your 75 oracle cards in Divinofax.

## 🎯 **Phase 1: Import Your Card Data (Now)**

### Step 1: Prepare Your CSV File
Create a CSV file with your 75 oracle cards using this format:

```csv
id,title,description,keywords
1,The Fool,Your card description here,keyword1,keyword2,keyword3
2,The Magician,Another card description,power,manifestation,will
...
75,The World,Final card description,completion,success,fulfillment
```

**Tips:**
- **ID**: Sequential numbers 1-75
- **Title**: Exact card name
- **Description**: 200-800 characters (optimal: 300-400)
- **Keywords**: Comma-separated mystical concepts

### Step 2: Import Your Cards
```bash
python3 manage_oracle_cards.py import --csv your_oracle_cards.csv
```

### Step 3: Verify Import
```bash
python3 manage_oracle_cards.py list
```

## 🏷️ **Phase 2: Add RFID Tags (When Ready)**

### Option A: Add Individual RFID Tags
```bash
# Add RFID tags one by one as you get them
python3 manage_oracle_cards.py add-rfid --id 1 --rfid "123456789001"
python3 manage_oracle_cards.py add-rfid --id 2 --rfid "123456789002"
```

### Option B: Bulk Import RFID Tags
Create a file called `rfid_tags.txt`:
```
1,123456789001
2,123456789002
3,123456789003
...
75,123456789075
```

Then import all at once:
```bash
python3 manage_oracle_cards.py bulk-rfid --file rfid_tags.txt
```

## 🚀 **Phase 3: Deploy to Divinofax**

### Deploy Your Cards
```bash
python3 manage_oracle_cards.py deploy
```

This creates:
- **Individual text files** for each card in `data/texts/`
- **RFID mapping file** at `data/rfid_mappings.json`
- **Backup** of previous data

## 📊 **Managing Your Cards**

### Check Status
```bash
python3 manage_oracle_cards.py list
```

Output:
```
ID   Title                     RFID Tag        Status  
------------------------------------------------------------
1    The Fool                  123456789001    Active  
2    The Magician              None            Active  
3    The High Priestess        123456789003    Active  
...

Summary: 75 total, 75 active, 45 with RFID tags
```

### Test Your Setup
```bash
# Test the Divinofax system
cd /Users/kathrynbennett/divinofax
source venv/bin/activate
SIMULATION_MODE=true python3 src/divinofax.py
```

## 📁 **File Structure After Setup**

```
data/
├── oracle_cards.json              # Master card database
├── rfid_mappings.json             # RFID → card mappings  
└── texts/                         # Individual card files
    ├── oracle_001_the_fool.txt
    ├── oracle_002_the_magician.txt
    └── ...
```

## 🔧 **Advanced Features**

### Backup System
- Automatic backups created on every save
- Files saved as `oracle_cards.backup.TIMESTAMP.json`

### Card Management
```bash
# Temporarily disable a card
# (Edit oracle_cards.json, set "active": false)

# Update a card description
# (Edit oracle_cards.json, then redeploy)

# Add new cards
# (Add to CSV and re-import, or edit JSON directly)
```

## 🎯 **Your Workflow**

1. **Today**: Create your CSV with all 75 cards and import
2. **Later**: Add RFID numbers as you get the physical tags
3. **Deploy**: Push everything to Divinofax system
4. **Test**: Run simulation mode to verify everything works
5. **Go Live**: Use with actual hardware!

## ⚡ **Quick Commands Reference**

```bash
# Import cards from CSV
python3 manage_oracle_cards.py import --csv my_cards.csv

# Add single RFID tag  
python3 manage_oracle_cards.py add-rfid --id 1 --rfid "123456789001"

# Bulk add RFID tags
python3 manage_oracle_cards.py bulk-rfid --file rfid_list.txt

# Deploy to Divinofax
python3 manage_oracle_cards.py deploy

# Check status
python3 manage_oracle_cards.py list

# Test system
SIMULATION_MODE=true python3 src/divinofax.py
```

Ready to set up your mystical oracle card collection! 🔮✨
