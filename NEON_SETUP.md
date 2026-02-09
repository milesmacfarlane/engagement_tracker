# Neon.tech PostgreSQL Setup Guide

## ✅ What You're Getting

- **Permanent Data Storage** - Never lost, even when app restarts
- **Professional Database** - PostgreSQL (industry standard)
- **FREE Tier** - 0.5GB storage, 100 hours compute/month (plenty for your needs)
- **Fast** - Optimized for performance
- **Reliable** - Automatic backups by Neon

---

## 🚀 Complete Setup (20 Minutes)

### Step 1: Create Neon Project (You're Here!)

On the Neon.tech screen you're on:

1. **Project name:** `engagement_tracker` ✅
2. **Postgres version:** 17 ✅
3. **Cloud provider:** AWS ✅
4. **Region:** AWS US West 2 (Oregon) ✅
5. **Enable Neon Auth:** Leave OFF (toggle gray)
6. Click **"Create Project"**

---

### Step 2: Copy Your Connection String

After project creates, you'll see a dashboard with:

**Connection string** (looks like this):
```
postgresql://username:password@ep-something-12345.us-west-2.aws.neon.tech/neondb?sslmode=require
```

**IMPORTANT:** 
1. Click the **"Copy"** button next to the connection string
2. Paste it somewhere safe (Notepad) - you'll need it in Step 4

---

### Step 3: Update Your Code

On your computer:

#### A. Replace database.py

```bash
cd C:\Users\micro\Desktop\engagement_tracker

# Backup old file
copy database.py database_csv_backup.py

# Replace with PostgreSQL version
copy database_postgresql.py database.py
```

#### B. Files Already Updated:
- ✅ requirements.txt (PostgreSQL dependencies added)
- ✅ database_postgresql.py (created)

---

### Step 4: Add Connection String to Streamlit Cloud

1. Go to: https://share.streamlit.io/
2. Click on your app: **wkengagement**
3. Click **"Settings"** (gear icon in top right)
4. Click **"Secrets"** in left sidebar
5. Paste this:

```toml
database_url = "postgresql://your-connection-string-here"
```

**Replace** `your-connection-string-here` with the connection string you copied in Step 2

**Example:**
```toml
database_url = "postgresql://neondb_owner:npg_abc123xyz@ep-cool-cloud-12345.us-west-2.aws.neon.tech/neondb?sslmode=require"
```

6. Click **"Save"**

---

### Step 5: Push Updated Code to GitHub

```bash
cd C:\Users\micro\Desktop\engagement_tracker

git add .
git commit -m "Add PostgreSQL database - permanent storage with Neon.tech"
git push
```

Streamlit Cloud will automatically redeploy (~2 minutes)

---

### Step 6: Initialize Database

1. Wait for app to redeploy
2. Go to: https://wkengagement.streamlit.app/
3. Navigate to **Setup** → **Data Management**
4. Click **"Generate Sample Data"**
5. You should see: ✅ "Created sample data"

**Test it:**
1. Go to Student Dashboard - see students
2. Refresh page (F5) - students still there! ✅
3. Wait 10 minutes, refresh - still there! ✅
4. **Data is permanent!**

---

## 🎯 What Just Happened?

### Before (CSV):
```
App restarts → Data deleted 💀
```

### After (PostgreSQL):
```
App restarts → Data still there! ✅
Week later → Data still there! ✅
Month later → Data still there! ✅
```

---

## 💾 How Data is Stored

```
Your Streamlit App
     ↓
Neon.tech PostgreSQL Database (Cloud)
     ↓
3 Tables:
  - students (student_id, name, primary_class)
  - classes (class_code, class_name)
  - observations (date, class_code, student_id, measure_name, value)
```

**All teachers using the app see the same data**

---

## 🔐 Security

### What's Protected:
- ✅ Connection encrypted (SSL)
- ✅ Password in connection string
- ✅ Only your app can access
- ✅ Neon automatic backups

### Access Control:
- Only people with Streamlit app URL can use it
- Can add authentication later if needed

---

## 📊 Neon.tech Free Tier Limits

**What you get FREE:**
- **Storage:** 0.5 GB (plenty - can store ~500,000 observations)
- **Compute:** 100 hours/month (more than enough)
- **Branches:** 10 (for testing)
- **History:** 7 days retention

**Your expected usage:**
- ~50 students per class
- ~3 classes
- ~20 observation days per month
- Total: ~2,700 observations/month
- **Well within free tier!**

---

## 🛠️ Managing Your Database

### View Data in Neon Console:

1. Go to: https://console.neon.tech/
2. Select your project: engagement_tracker
3. Click **"SQL Editor"** (left sidebar)
4. Run queries:

```sql
-- See all students
SELECT * FROM students;

-- See recent observations
SELECT * FROM observations 
ORDER BY date DESC 
LIMIT 100;

-- Count observations by date
SELECT date, COUNT(*) as obs_count 
FROM observations 
GROUP BY date 
ORDER BY date DESC;
```

### Backup Your Data:

**Option 1: From App**
- Setup → Data Management → Export All Data
- Downloads CSV files

**Option 2: From Neon**
- Neon automatically backs up
- Can restore from backup if needed

---

## ⚠️ Troubleshooting

### Error: "Database connection error"

**Problem:** Can't connect to Neon

**Solutions:**
1. Check connection string in Streamlit secrets
2. Make sure you copied entire string (including password)
3. Check Neon project is active (not suspended)

### Error: "relation 'students' does not exist"

**Problem:** Tables not created

**Solution:**
1. Go to Setup → Data Management
2. Click "Generate Sample Data"
3. This creates tables automatically

### Data Disappeared

**Problem:** Actually shouldn't happen with PostgreSQL!

**Check:**
1. Are you looking at right deployment?
2. Did someone delete data?
3. Check Neon console - data should be there

---

## 🎓 For Multiple Teachers

### Current Setup:
- All teachers see same data
- Collaborative

### To Add User Accounts Later:
1. Add authentication (Streamlit authenticator)
2. Add user_id column to tables
3. Filter data by user_id

**For now:** All teachers share same database (collaborative model)

---

## 💡 Tips

### Best Practices:
1. **Regular exports** - Backup CSV weekly
2. **Monitor usage** - Check Neon dashboard monthly
3. **Clean old data** - Delete observations from previous years

### What to Monitor:
- Storage usage (should stay under 100MB)
- Compute hours (should stay under 100/month)

---

## 📈 Scaling Up

If you exceed free tier limits:

**Neon Paid Plans:**
- Launch: $19/month (10GB storage, unlimited compute)
- Scale: $69/month (50GB storage)

**You won't need paid unless:**
- 10+ schools using it
- 10+ years of data stored
- Very unlikely!

---

## 🆘 Need Help?

### Common Issues:

**Issue:** Connection string has special characters
**Fix:** Make sure entire string is in quotes in secrets

**Issue:** App won't deploy after update
**Fix:** Check Streamlit logs for errors

**Issue:** Forgot connection string
**Fix:** Get it from Neon dashboard → Connection Details

---

## ✅ Verification Checklist

After setup, verify:

- [ ] Neon project created
- [ ] Connection string copied
- [ ] Code updated (database.py replaced)
- [ ] Pushed to GitHub
- [ ] Added connection string to Streamlit secrets
- [ ] App redeployed successfully
- [ ] Sample data generated
- [ ] Data persists after refresh
- [ ] Can view data in Neon console

---

## 🎉 You're Done!

Your engagement tracker now has:
- ✅ Permanent data storage
- ✅ Professional database
- ✅ No data loss on restarts
- ✅ FREE (within limits)
- ✅ Fast and reliable

**Next:** Start using it! All your observations will be saved permanently.

---

**Setup Time:** ~20 minutes  
**Cost:** $0 (FREE tier)  
**Data Loss Risk:** None! ✅
