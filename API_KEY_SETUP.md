# Where to Place Your Claude API Key

You have **two options** for providing your Claude API key:

## Option 1: Interactive Entry (Recommended for First-Time Use)

Simply run the application and enter your API key when prompted:

```bash
python main.py
```

The application will ask:
```
Enter Claude API key:
```

Paste your API key (starts with `sk-ant-`) and press Enter.

## Option 2: Environment Variables (Recommended for Repeated Use)

### Step 1: Create a `.env` file

Copy the example file:
```bash
cp .env.example .env
```

Or create a new file named `.env` in the project root directory.

### Step 2: Add Your API Key

Edit the `.env` file and add your Claude API key:

```bash
CLAUDE_API_KEY=sk-ant-your-actual-api-key-here
AZURE_CLIENT_ID=your-client-id
AZURE_TENANT_ID=your-tenant-id
SENDER_EMAIL=your-email@example.com
RECIPIENT_EMAIL=recipient@example.com
```

### Step 3: Run the Application

The application will automatically read from `.env` if it exists (future enhancement - currently prompts interactively).

## Getting Your Claude API Key

1. Go to [Anthropic Console](https://console.anthropic.com/)
2. Sign in or create an account
3. Navigate to **API Keys** section
4. Click **Create Key**
5. Copy the key (it starts with `sk-ant-`)
6. Save it securely - you won't be able to see it again!

## Security Notes

- **Never commit your `.env` file to git** - it's already in `.gitignore`
- Your API key is masked in log files (shows as `sk-ant-...xyz123`)
- Keep your API key secret and don't share it
- If your key is compromised, delete it in the Anthropic Console and create a new one

## Model Information

The application uses **Claude 3.5 Haiku** - the most cost-effective Claude model:

- **Model**: `claude-3-5-haiku-20241022`
- **Input tokens**: $0.80 per 1M tokens
- **Output tokens**: $4.00 per 1M tokens
- **Estimated cost per email**: ~$0.0005-0.001
- **For 100 emails**: ~$0.05-0.10

You can change the model in `content_generator.py` if you want to use a different Claude model (e.g., Claude 3.5 Sonnet for higher quality).
