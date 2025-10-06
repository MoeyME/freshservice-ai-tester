# 🚀 Ready to Run!

Your IT Ticket Email Generator is fully configured and ready to use.

## ✅ Configuration Complete

All your credentials are loaded from `.env.example`:
- ✓ Claude API Key configured
- ✓ Azure Client ID configured
- ✓ Azure Tenant ID configured
- ✓ Sender Email configured
- ✓ Recipient Email configured

## 📊 Data Files Loaded

- ✓ **273 hierarchical categories** from `categories.csv`
  - Format: Category > Sub-Category > Item
  - Example: "Application Support > Frameworks > Support"

- ✓ **4 Priority levels** from `priorities_and_types.md`
  - Priority 1 (URGENT) - 10%
  - Priority 2 (HIGH) - 20%
  - Priority 3 (MEDIUM) - 40%
  - Priority 4 (LOW) - 30%

- ✓ **2 Ticket types**
  - Incident - 60%
  - Service Request - 40%

## 🎯 How to Run

Simply execute:

```bash
python main.py
```

The application will:
1. ✓ Auto-load all credentials from `.env.example`
2. ✓ Load your 273 categories from CSV
3. ✓ Load priority levels from markdown
4. ✓ Ask how many emails to generate
5. ✓ Show distribution summary
6. ✓ Ask for confirmation
7. ✓ Authenticate with Microsoft (device code flow)
8. ✓ Generate realistic emails using Claude 3.5 Haiku
9. ✓ Send emails with 10-second delays
10. ✓ Create detailed log file

## 💡 What to Expect

### Costs (Claude 3.5 Haiku)
- ~$0.0005-0.001 per email
- 100 emails ≈ $0.05-0.10

### Authentication
You'll need to:
1. Visit the URL shown
2. Enter the device code
3. Sign in with your Microsoft account (mohammed.el-cheikh@dahlsens.com.au)

### Email Generation
Claude will generate realistic emails like:
- "My laptop keeps blue screening" (Hardware > Hardware Troubleshooting > Laptop, Priority 2, Incident)
- "Request access to former employee's OneDrive" (User Administration > Permissions & Access Rights, Priority 3, Service Request)
- "Point of Sale terminal not responding at checkout" (Application Support > Frameworks > Point Of Sale, Priority 1, Incident)

### Results
You'll get:
- Console output with real-time progress
- Log file: `email_test_log_YYYYMMDD_HHMMSS.txt`
- Summary statistics
- Cost estimation

## 📝 Example Run

```
IT TICKET EMAIL GENERATOR
✓ Loaded configuration from .env.example

STEP 1: Configuration
Microsoft Azure Configuration:
Enter Azure Client ID: b060dd17-ce88-46ff-a238-958e6f328f4a
Enter Azure Tenant ID: f86c2d5f-b962-48fa-8af9-68ccebd36fa3
Enter your email address: mohammed.el-cheikh@dahlsens.com.au
Enter recipient email address: itsupport@jcdahlsengroup.com.au

Claude API Configuration:
Enter Claude API key: sk-ant-...ke8_A

STEP 2: Loading Data Files
✓ Loaded 273 categories from categories.csv
✓ Loaded 4 priorities and 2 types from priorities_and_types.md

STEP 3: Email Count
How many test emails to generate? 10

Distribution Summary:
Priorities:
  Priority 1: 1 (10.0%)
  Priority 2: 2 (20.0%)
  Priority 3: 4 (40.0%)
  Priority 4: 3 (30.0%)

Types:
  Incident: 6 (60.0%)
  Service Request: 4 (40.0%)

STEP 4: Confirmation
Ready to generate and send 10 emails
From: mohammed.el-cheikh@dahlsens.com.au
To:   itsupport@jcdahlsengroup.com.au

Proceed with email generation and sending? (y/n): y
...
```

## 🎉 You're All Set!

Just run: `python main.py`
