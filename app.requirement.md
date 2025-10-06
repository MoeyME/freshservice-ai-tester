### 3. Confirmation
Ask user to confirm before sending (show total count and recipient)

### 4. Generation Phase
Show progress as content is being generated:
- "Generating email content 1 of 10..."
- Handle and display any API errors gracefully

### 5. Sending Phase
Show real-time progress with:
- Current email being sent (X of Y)
- Countdown timer during 10-second waits
- Success/failure indicator for each email

### 6. Results Summary
After completion, display:
- Total sent successfully
- Any failures (with error details)
- Estimated DeepSeek API cost
- Location of log file
- Distribution summary (priorities and types)

## Logging

Create a detailed log file: `email_test_log_YYYYMMDD_HHMMSS.txt` containing:

- Timestamp of test run
- Configuration used:
  - Microsoft authentication details (client ID, tenant, email address)
  - Number of emails requested
  - DeepSeek API key (masked, e.g., "sk-...xyz123")
- For each email sent:
  - Email number
  - Category targeted
  - Type (Incident/Service Request)
  - Priority level targeted
  - Full subject line
  - Full description text
  - Timestamp sent
  - Success/failure status
  - Blank line for manual ticket number entry: "Ticket #: ___________"
  - Separator line between emails for readability
- Summary statistics at the end:
  - Total sent
  - Success count
  - Failure count
  - Distribution breakdown (count per priority level, count per type)
  - Estimated API cost

## Technical Requirements

- Create `requirements.txt` with needed packages:
  - msal (Microsoft authentication)
  - requests (API calls)
  - Any other dependencies
- Use Python 3.8+ features
- Include comprehensive error handling:
  - Missing/malformed CSV file
  - Missing/malformed markdown file
  - Invalid API keys
  - DeepSeek API failures (rate limits, network errors, invalid responses)
  - Microsoft authentication failures
  - Network errors during email sending
  - Graph API errors
  - Invalid user input (non-numeric email count, zero or negative numbers)
- Clear, helpful error messages that guide the user on how to fix issues
- Modular code structure:
  - Separate functions for: authentication (both APIs), file reading, content generation, email sending, logging, display formatting
  - Keep DeepSeek prompts in easily editable string templates so they can be modified without changing code logic
- Add comments explaining:
  - OAuth flow and Graph API calls
  - DeepSeek API integration
  - Content generation strategy

## Code Quality

- Use type hints where appropriate
- Validate API responses before using them
- Include a comprehensive `README.md` explaining:
  - **Prerequisites:**
    - Azure app registration setup (step-by-step with required permissions)
    - DeepSeek API key acquisition
  - **Setup:**
    - Installing dependencies
    - Setting environment variables (optional)
  - **File format expectations:**
    - Example categories.csv format
    - Example priorities_and_types.md structure
  - **How to run:**
    - Step-by-step execution flow
    - What to expect at each stage
  - **Troubleshooting:**
    - Common errors and solutions
    - API rate limit handling
    - Authentication issues

## DeepSeek API Integration Details

- Use the DeepSeek Chat API endpoint
- Use an appropriate model (e.g., deepseek-chat or deepseek-reasoner based on what's available)
- Set reasonable parameters (temperature ~0.8-0.9 for variety)
- Keep token usage reasonable (aim for ~200-300 tokens per email generation)
- Handle API errors gracefully with informative messages
- Track total tokens used for cost estimation
- Add a small delay between DeepSeek API calls if generating multiple emails rapidly

## Cost Tracking

- Track total tokens used across all DeepSeek API calls
- Calculate and display estimated cost based on DeepSeek pricing
- Include this in both console output and log file

---

**Goal**: Create realistic, varied test data that authentically challenges an IT agent's ability to correctly categorize, prioritize, and route tickets based solely on the content - exactly as they would with real user submissions.