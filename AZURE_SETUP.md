# Azure App Registration Setup Guide

The authentication error you're seeing means your Azure app needs to be configured for **public client authentication** (device code flow).

## Error Received
```
AADSTS7000218: The request body must contain the following parameter: 'client_assertion' or 'client_secret'
```

This happens when the app is configured as a **Web app** instead of a **Public client**.

## Fix: Configure Azure App Registration

### Step 1: Go to Azure Portal
1. Visit [Azure Portal](https://portal.azure.com)
2. Navigate to **Azure Active Directory**
3. Click **App registrations**
4. Find your app: Look for Client ID `b060dd17-ce88-46ff-a238-958e6f328f4a`

### Step 2: Enable Public Client Flow

1. In your app registration, click on **Authentication** in the left menu
2. Scroll down to **Advanced settings**
3. Find **Allow public client flows**
4. Toggle it to **Yes**
5. Click **Save** at the top

### Step 3: Verify API Permissions

1. Click on **API permissions** in the left menu
2. Make sure you have these permissions:
   - **Microsoft Graph** → **Delegated permissions** → **Mail.Send**
3. If not present, click **Add a permission**:
   - Select **Microsoft Graph**
   - Select **Delegated permissions**
   - Search for and select **Mail.Send**
   - Click **Add permissions**
4. Click **Grant admin consent** (requires admin)

### Step 4: Verify Supported Account Types

1. Click on **Overview** in the left menu
2. Under **Essentials**, check **Supported account types**
3. It should be set to one of:
   - **Accounts in this organizational directory only (Dahlsens only - Single tenant)**
   - **Accounts in any organizational directory (Any Azure AD directory - Multitenant)**

### Step 5: Add Redirect URI (Optional but Recommended)

1. Click on **Authentication**
2. Under **Platform configurations**, click **Add a platform**
3. Select **Mobile and desktop applications**
4. Check the box for: `https://login.microsoftonline.com/common/oauth2/nativeclient`
5. Click **Configure**

## Alternative: Create a New App Registration

If you don't have permissions to modify the existing app, create a new one:

### 1. Create New App
- Go to **App registrations** → **New registration**
- Name: `IT Ticket Email Generator`
- Supported account types: **Accounts in this organizational directory only**
- Click **Register**

### 2. Note the IDs
- Copy the **Application (client) ID**
- Copy the **Directory (tenant) ID**
- Update these in your `.env.local` file

### 3. Configure Authentication
- Go to **Authentication**
- Enable **Allow public client flows** → **Yes**
- Add platform → **Mobile and desktop applications**
- Select: `https://login.microsoftonline.com/common/oauth2/nativeclient`

### 4. Add Permissions
- Go to **API permissions**
- Add permission → **Microsoft Graph** → **Delegated permissions**
- Select: **Mail.Send**
- Click **Grant admin consent**

## After Configuration

Once configured, run the application again:

```bash
python main.py
```

You should see:
```
MICROSOFT AUTHENTICATION REQUIRED
============================================================
To sign in, use a web browser to open the page https://microsoft.com/devicelogin
and enter the code XXXXXXXXX to authenticate.
============================================================
```

Then:
1. Open the URL in a browser
2. Enter the code shown
3. Sign in with your Microsoft account (mohammed.el-cheikh@dahlsens.com.au)
4. Grant the requested permissions
5. Return to the terminal - authentication will complete automatically

## Troubleshooting

**Issue**: Still getting client_secret error
- **Solution**: Make sure you saved the "Allow public client flows" setting

**Issue**: Access denied error
- **Solution**: Ask your admin to grant consent for Mail.Send permission

**Issue**: Invalid client error
- **Solution**: Double-check the Client ID and Tenant ID are correct

**Issue**: User doesn't have mailbox
- **Solution**: Make sure the sender email (mohammed.el-cheikh@dahlsens.com.au) has a valid Microsoft 365 mailbox

## Need Help?

Contact your IT administrator or Azure AD admin to help configure the app registration with the settings above.
