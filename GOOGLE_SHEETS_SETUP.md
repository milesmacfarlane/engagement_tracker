# Google Sheets Integration Setup Guide

## Overview

This system allows **each teacher to have their own Google Sheet** for storing student data. Data is persistent, backed up by Google, and accessible from anywhere.

## ✅ Benefits

- 📊 **Your Own Sheet** - Each teacher gets their own private Google Sheet
- 💾 **Never Lost** - Data is permanent, even when app restarts
- 🔄 **Real-Time** - See changes immediately
- 👥 **Collaborative** - Multiple teachers can observe simultaneously
- 📱 **Accessible** - View/edit data in Google Sheets anytime
- 🆓 **FREE** - No cost, uses your Google account

---

## 🚀 Quick Setup (15 minutes)

### For Administrators: One-Time Setup

#### Step 1: Create Google Cloud Project

1. Go to: https://console.cloud.google.com/
2. Click "Select a project" → "New Project"
3. Name it: "Engagement Tracker"
4. Click "Create"

#### Step 2: Enable Google Sheets API

1. In the project, go to "APIs & Services" → "Enable APIs and Services"
2. Search for: "Google Sheets API"
3. Click it → Click "Enable"
4. Also search for and enable: "Google Drive API"

#### Step 3: Create Service Account

1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "Service Account"
3. Name: "engagement-tracker-service"
4. Click "Create and Continue"
5. Skip optional steps → "Done"

#### Step 4: Create Service Account Key

1. Click on the service account you just created
2. Go to "Keys" tab
3. Click "Add Key" → "Create new key"
4. Choose "JSON"
5. Click "Create" - **File downloads automatically**
6. **SAVE THIS FILE SECURELY** - you'll need it!

#### Step 5: Add Credentials to Streamlit Cloud

1. Go to your Streamlit Cloud dashboard
2. Click on your app
3. Click "Settings" (gear icon)
4. Go to "Secrets"
5. Paste this structure:

```toml
[gcp_service_account]
type = "service_account"
project_id = "your-project-id"
private_key_id = "your-private-key-id"
private_key = "-----BEGIN PRIVATE KEY-----\nYour\nPrivate\nKey\nHere\n-----END PRIVATE KEY-----\n"
client_email = "engagement-tracker-service@your-project.iam.gserviceaccount.com"
client_id = "your-client-id"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "your-cert-url"
```

**Copy values from the JSON file you downloaded in Step 4**

6. Click "Save"

---

### For Teachers: Connecting Your Sheet

#### Step 1: Create Your Google Sheet

1. Go to: https://sheets.google.com/
2. Click "+ Blank" to create new sheet
3. Name it: "My Student Engagement Data"
4. **Copy the URL** - you'll need this

#### Step 2: Share Sheet with Service Account

1. In your Google Sheet, click "Share" (top right)
2. In the email field, paste the service account email:
   ```
   engagement-tracker-service@your-project.iam.gserviceaccount.com
   ```
   _(You'll see this email in the app)_
3. Change permission to **"Editor"**
4. Uncheck "Notify people"
5. Click "Share"

#### Step 3: Connect in App

1. Open the Engagement Tracker app
2. Go to "Setup" page
3. Scroll to "Google Sheets Connection"
4. Paste your Google Sheet URL
5. Click "Connect Sheet"
6. You should see: ✅ "Connected to: [Your Sheet Name]"

#### Step 4: Start Using!

The app will now:
- ✅ Save all data to YOUR Google Sheet
- ✅ Create 3 worksheets: students, classes, observations
- ✅ Keep data synchronized

---

## 📊 How It Works

### Data Structure

Your Google Sheet will have 3 worksheets:

#### 1. students
```
student_id | name          | primary_class
-----------|---------------|-------------
100001     | Alice Smith   | HIS20A
100002     | Bob Jones     | HIS20A
```

#### 2. classes
```
class_code | class_name
-----------|---------------------------
HIS20A     | History 20 Section A
HIS20B     | History 20 Section B
```

#### 3. observations
```
date       | class_code | student_id | measure_name  | value
-----------|------------|------------|---------------|------
2026-01-15 | HIS20A     | 100001     | Time on Task  | 1
2026-01-15 | HIS20A     | 100001     | Asked/Answ... | 0
```

### Automatic Sync

- **Save observations** → Instantly written to your sheet
- **Add students** → Immediately appears in sheet
- **View in Google Sheets** → See all your data
- **Edit in Google Sheets** → App reads changes (refresh needed)

---

## 🔐 Security & Privacy

### Who Can Access?

**Your Google Sheet:**
- ✅ You (owner)
- ✅ Service account (automated access only)
- ✅ Anyone you explicitly share with

**The App:**
- Can ONLY access sheets shared with the service account
- Cannot see other teachers' sheets
- Cannot access your other Google files

### FERPA Compliance

- ✅ Data stored in your Google Drive
- ✅ Controlled by your school's Google Workspace
- ✅ Subject to your organization's data policies
- ✅ Can be deleted anytime by you

### Best Practices

1. **Don't share** your sheet publicly
2. **Use school Google account** (not personal)
3. **Regular backups** - File → Download as Excel
4. **Restrict sharing** - Only share with authorized staff

---

## 🎯 Multiple Teachers / Collaborative Use

### Option 1: Each Teacher Has Own Sheet (Recommended)

Each teacher:
1. Creates their own Google Sheet
2. Shares it with service account
3. Connects to their sheet in the app
4. Has completely separate data

**Pros:**
- Complete independence
- No conflicts
- Each teacher controls their data

---

### Option 2: Shared Sheet for Team

One teacher creates sheet, shares with both:
- Service account (Editor)
- Other teachers (Editor)

All teachers connect to **same sheet URL**

**Pros:**
- Collaborative observation
- See all class data together
- Single source of truth

**Cons:**
- Need to coordinate who enters data
- Possible conflicts if editing simultaneously

---

## 🛠️ Troubleshooting

### Error: "Sheet not found"

**Problem:** App can't access your sheet

**Solutions:**
1. Check you shared with correct service account email
2. Gave "Editor" permission (not "Viewer")
3. Sheet URL is correct
4. Sheet is not deleted

### Error: "API Error"

**Problem:** Google API issue

**Solutions:**
1. Check Google Sheets API is enabled in Cloud Console
2. Check Google Drive API is enabled
3. Service account credentials are correct
4. Try reconnecting

### Error: "Credentials not configured"

**Problem:** Service account not set up in Streamlit Cloud

**Solution:** Administrator needs to add credentials to Streamlit secrets (see Step 5 above)

### Changes Don't Appear

**Problem:** App showing old data

**Solution:** 
1. Refresh the page (F5)
2. App reads from sheet on page load
3. Or click "Refresh Data" button if available

---

## 📋 Switching Between Storage Methods

### Currently Using CSV (Temporary)?

When you connect Google Sheets:
1. App will use Google Sheets going forward
2. Old CSV data is NOT automatically migrated
3. **To migrate**: Export CSVs → Import to new sheet

### Want to Go Back to CSV?

1. Click "Disconnect" in Setup
2. App reverts to CSV files
3. Google Sheet data remains (not deleted)
4. Can reconnect anytime

---

## 💡 Tips & Tricks

### Backup Your Data

Even with Google Sheets, create backups:
1. Open your Google Sheet
2. File → Download → Excel (.xlsx)
3. Save to your computer monthly

### View Data in Sheets

You can:
- ✅ View data anytime
- ✅ Create pivot tables
- ✅ Add charts
- ✅ Export reports
- ❌ Don't manually edit (can cause conflicts)

### Organizing Your Sheet

Consider:
- **Coloring rows** - Color-code classes
- **Freezing headers** - View → Freeze → 1 row
- **Filtering** - Add filters to find students quickly

### Sharing Reports

From Google Sheets:
1. Create view-only link
2. Share with parents/admin
3. They can't edit, only view

---

## 🆘 Getting Help

### For Teachers:

Contact your school's IT administrator or the teacher who set up the system.

### For Administrators:

1. Check Streamlit Cloud logs (Settings → Logs)
2. Verify service account has correct permissions
3. Test with a simple sheet first
4. Review Google Cloud Console for API errors

---

## 📚 Additional Resources

- Google Sheets API: https://developers.google.com/sheets/api
- Service Accounts: https://cloud.google.com/iam/docs/service-accounts
- Streamlit Secrets: https://docs.streamlit.io/streamlit-community-cloud/get-started/deploy-an-app/connect-to-data-sources/secrets-management

---

## ✅ Checklist

**Administrator Setup:**
- [ ] Create Google Cloud Project
- [ ] Enable Google Sheets API
- [ ] Enable Google Drive API
- [ ] Create Service Account
- [ ] Download JSON key
- [ ] Add credentials to Streamlit Secrets
- [ ] Share service account email with teachers

**Teacher Setup:**
- [ ] Create Google Sheet
- [ ] Share with service account (Editor)
- [ ] Copy sheet URL
- [ ] Connect in app
- [ ] Test by adding sample data
- [ ] Verify data appears in sheet

---

**Version:** 1.3.0  
**Feature:** Google Sheets Integration  
**Status:** Ready to Deploy
