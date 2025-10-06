# IT Ticket Email Generator

A Python application that generates and sends realistic IT support ticket emails for testing purposes. Uses Microsoft Graph API for email delivery and Claude AI for content generation.

## Features

- 🤖 AI-powered realistic ticket content generation
- 📧 Automated email sending via Microsoft Graph API
- 📊 Intelligent distribution across priorities and ticket types
- 📝 Comprehensive logging with manual ticket number tracking
- ⏱️ Built-in rate limiting (10-second delays between emails)
- 💰 Cost tracking for Claude API usage
- ✅ Real-time progress display

## Prerequisites

### 1. Python 3.8+

Make sure you have Python 3.8 or higher installed.

### 2. Azure App Registration

You need to register an application in Azure Active Directory:

1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to **Azure Active Directory** > **App registrations**
3. Click **New registration**
4. Enter a name (e.g., "IT Ticket Generator")
5. Select **Accounts in this organizational directory only**
6. Click **Register**
7. Note down the **Application (client) ID** and **Directory (tenant) ID**

#### Configure API Permissions:

1. In your app registration, go to **API permissions**
2. Click **Add a permission**
3. Select **Microsoft Graph**
4. Choose **Delegated permissions**
5. Add the following permission:
   - `Mail.Send` - Send mail as a user
6. Click **Add permissions**
7. Click **Grant admin consent** (requires admin rights)

### 3. Claude API Key

1. Sign up at [Anthropic Console](https://console.anthropic.com/)
2. Navigate to API Keys section
3. Create a new API key
4. Copy and save the key (starts with `sk-ant-`)

## Installation

1. Clone or download this repository

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. **(Optional)** Configure environment variables:
   - Copy `.env.example` to `.env`
   - Fill in your API keys and configuration
   - The application will use these values automatically if present
   - Otherwise, you'll be prompted to enter them interactively

## Configuration Files

The application requires two configuration files:

### categories.csv

CSV file containing IT ticket categories. Example:

```csv
Category
Hardware
Software
Network
Email
Password Reset
Access Request
Printer
VPN
Application Error
System Performance
```

A sample file is already included in the repository.

### priorities_and_types.md

Markdown file defining priority levels and ticket types. Example structure:

```markdown
# IT Ticket Priorities and Types

## Priority Levels

### P1 - Critical
- System down affecting multiple users
- Security breach

### P2 - High
- Major functionality impaired
- Affecting department or team

### P3 - Medium
- Minor functionality issue
- Affecting individual user

### P4 - Low
- Cosmetic issues
- Feature requests

## Ticket Types

### Incident
Issues, problems, errors, or outages requiring resolution

### Service Request
Requests for new access, changes, or standard services
```

A sample file is already included in the repository.

## Usage

### Basic Usage

Run the application:

```bash
python main.py
```

The application will guide you through the following steps:

1. **Configuration**: Enter Azure and DeepSeek credentials
2. **Load Data**: Automatically loads categories and priorities
3. **Email Count**: Specify how many test emails to generate
4. **Confirmation**: Review settings before proceeding
5. **Authentication**: Complete Microsoft OAuth flow
6. **Generation**: AI generates email content
7. **Sending**: Sends emails with 10-second delays
8. **Results**: View summary and log file location

### Interactive Prompts

The application will ask for:

- **Azure Client ID**: Your Azure app's Application (client) ID
- **Azure Tenant ID**: Your Azure directory's Tenant ID
- **Your Email**: The email address to send from (must match authenticated user)
- **Recipient Email**: Where to send the test emails
- **Claude API Key**: Your Claude API key

### Authentication Flow

The application uses **device code flow** for authentication:

1. You'll be shown a URL and code
2. Visit the URL in a browser
3. Enter the code when prompted
4. Sign in with your Microsoft account
5. Grant the requested permissions

## Output

### Console Output

Real-time progress display showing:
- Configuration validation
- Data loading status
- Email generation progress
- Email sending progress with countdown
- Success/failure for each email
- Final statistics and cost estimation

### Log File

A detailed log file is created: `email_test_log_YYYYMMDD_HHMMSS.txt`

The log includes:
- Run configuration (with masked API keys)
- Individual email details:
  - Category, type, priority
  - Subject and description
  - Timestamp and status
  - Blank line for manual ticket number: `Ticket #: ___________`
- Summary statistics:
  - Success/failure counts
  - Priority distribution
  - Type distribution
  - Claude API cost

## Ticket Distribution

The application creates a realistic distribution:

- **P1 (Critical)**: 10%
- **P2 (High)**: 20%
- **P3 (Medium)**: 40%
- **P4 (Low)**: 30%

- **Incident**: 60%
- **Service Request**: 40%

Categories are distributed evenly across all defined categories.

## Error Handling

The application handles various error scenarios:

### File Errors
- Missing CSV or markdown files
- Invalid file formats
- Empty or malformed data

### API Errors
- Invalid credentials
- Authentication failures
- Network timeouts
- Rate limiting (with automatic retry)
- DeepSeek API errors

### Validation Errors
- Invalid email formats
- Malformed GUIDs for Azure IDs
- Invalid API key format
- Invalid email counts

## Troubleshooting

### Authentication Issues

**Problem**: "Authentication failed" or "invalid_client"

**Solutions**:
- Verify Client ID and Tenant ID are correct
- Ensure app has Mail.Send permission
- Check that admin consent was granted
- Verify you're using the correct Microsoft account

### Email Sending Issues

**Problem**: Emails not sending or "403 Forbidden"

**Solutions**:
- Ensure the authenticated user matches the sender email
- Verify Mail.Send permission is granted
- Check that the mailbox is enabled
- Ensure you have a valid Microsoft 365 license

### Claude API Issues

**Problem**: "Rate limit exceeded" or API errors

**Solutions**:
- Check API key is valid and active
- Verify you have sufficient credits
- Wait a few minutes if rate limited
- Check Anthropic service status

### Content Generation Issues

**Problem**: Generated content is malformed

**Solutions**:
- The application has retry logic (3 attempts)
- Check Claude API response in error messages
- Verify network connectivity

## File Structure

```
.
├── main.py                      # Main application entry point
├── auth.py                      # Microsoft authentication module
├── content_generator.py         # Claude AI integration
├── email_sender.py              # Email sending via Graph API
├── logger.py                    # Logging system
├── utils.py                     # Utility functions
├── requirements.txt             # Python dependencies
├── categories.csv               # IT ticket categories
├── priorities_and_types.md      # Priority levels and types
├── .gitignore                   # Git ignore rules
└── README.md                    # This file
```

## Cost Estimation

Claude API pricing for Claude 3.5 Haiku (cheapest model):
- Input tokens: $0.80 per 1M tokens
- Output tokens: $4.00 per 1M tokens

Typical cost per email: ~$0.0005-0.001

For 100 emails: ~$0.05-0.10

## Security Notes

- API keys are masked in log files (shows only first 3 and last 6 characters)
- Never commit credentials to version control
- The `.gitignore` is configured to exclude sensitive files
- Use environment variables for automation if needed

## Limitations

- Maximum 1000 emails per run (configurable in code)
- 10-second delay between emails (per requirements)
- Requires interactive authentication (device code flow)
- Claude API requires internet connectivity

## License

This project is provided as-is for testing purposes.

## Support

For issues or questions:
1. Check this README's Troubleshooting section
2. Review error messages in console and log files
3. Verify all prerequisites are met
4. Check Azure and Anthropic service status
