# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python application for generating and sending realistic IT support ticket test emails using Microsoft Graph API and Claude AI for content generation. The tool creates varied test data to challenge IT agent categorization systems.

## Architecture

The application follows this workflow:
1. **Authentication**: OAuth flow for Microsoft Graph API + Claude API key authentication
2. **Input Processing**: Read categories from CSV and priority/type data from markdown
3. **Content Generation**: Use Claude API to generate realistic email content (subject + description)
4. **Email Sending**: Send via Microsoft Graph API with 10-second delays between emails
5. **Logging**: Comprehensive logging to `email_test_log_YYYYMMDD_HHMMSS.txt`

### Key Components (to be implemented)

- **Authentication Module**: Handle Microsoft OAuth flow and Claude API authentication
- **File Readers**: Parse `categories.csv` and `priorities_and_types.md`
- **Content Generator**: Interface with Claude API to create email content
- **Email Sender**: Use Microsoft Graph API to send emails
- **Logger**: Create detailed log files with ticket tracking
- **Progress Display**: Real-time console feedback during generation and sending phases

## Development Commands

Since the project is not yet implemented, typical commands will be:

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py  # or whatever the main entry point is named
```

## Input File Formats

### categories.csv
CSV file containing IT support ticket categories (structure to be defined)

### priorities_and_types.md
Markdown file defining priority levels and ticket types (Incident/Service Request)

## API Integration

### Microsoft Graph API
- Requires Azure app registration with appropriate permissions
- Uses OAuth authentication flow
- Sends emails on behalf of authenticated user

### Claude API
- Endpoint: https://api.anthropic.com/v1/messages
- Model: claude-3-5-haiku-20241022 (cheapest option)
- Temperature: 0.8-0.9 for content variety
- Target: ~200-400 tokens per email generation
- Cost tracking required for all API calls
- Pricing: $0.80 per 1M input tokens, $4.00 per 1M output tokens

## Key Requirements

- Python 3.8+
- Error handling for: CSV/markdown parsing, API failures, network errors, invalid inputs
- Claude prompts should be kept in editable string templates
- Type hints throughout code
- 10-second delay between email sends (hard requirement)
- Comprehensive logging with manual ticket number entry fields
- Real-time progress indicators during generation and sending

## Output

The log file must include:
- Configuration (with masked API keys)
- Per-email details: category, type, priority, subject, description, timestamp, status
- Blank line for manual ticket entry: "Ticket #: ___________"
- Summary statistics: total sent, success/failure counts, distribution breakdown, API cost estimate
