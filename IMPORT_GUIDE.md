# Quick Import Guide - Sample Data

## 📥 How to Import Your Sample Data

### Step 1: Update Your Code (Do This First!)

The observations import feature was just added. Update your local code:

```bash
cd C:\Users\micro\Desktop\engagement_tracker

# Pull the updated setup.py (with observations import)
# Copy the new setup.py to pages/setup.py

git add .
git commit -m "Add bulk observations import feature"
git push
```

Wait for Streamlit Cloud to redeploy (~2 minutes)

---

### Step 2: Import in Order

Go to: https://wkengagement.streamlit.app/

#### A. Import Classes First
1. Go to **Setup** → **Classes** tab
2. Click **"Choose File"**
3. Upload `classes.csv`
4. Click **Import**

#### B. Import Students Second
1. Go to **Setup** → **Student Roster** tab
2. Scroll to **"Bulk Import Students"**
3. Click **"Choose File"**
4. Upload `students.csv`
5. Click **"✅ Import Students"**

#### C. Import Observations Last
1. Go to **Setup** → **Data Management** tab
2. Scroll to **"📥 Import Observations"** (new section!)
3. Click **"Choose File"**
4. Upload `observations.csv`
5. Review the preview (shows first 10 rows)
6. Click **"✅ Import Observations"**
7. Wait for success message

---

### Step 3: Explore the Data!

Now you can:
- **Class Dashboard** - See all 28 students, performance distribution
- **Student Dashboard** - Compare Perry Present vs Noah Noshow
- **Reports** - Generate PDFs showing different patterns
- **Quick Entry Log** - Add new observations

---

## ⚡ Quick Import Summary

**Total time:** ~5 minutes

1. Classes CSV → Setup → Classes tab
2. Students CSV → Setup → Student Roster tab  
3. Observations CSV → Setup → Data Management tab (NEW!)

**Result:** 28 students, 20 days of observations, ready to explore!

---

## 🎯 What to Look For

### In Class Dashboard:
- **Performance bands**: Should see distribution from Exemplary to Needs Support
- **Students needing attention**: Perry Present, Neddy Naptime, others
- **Class average**: ~62% achievement

### In Student Dashboards:
- **Perry Present (5555555)**: 90% attendance, 27% achievement
- **Noah Noshow (1000004)**: 30% attendance, 53% achievement
- **Tyler Tries (9999994)**: High help-seeking, low completion

### In Reports:
- Generate PDF for any student
- See measure-by-measure breakdown
- Notice strengths and focus areas

---

## 🔄 If Import Doesn't Work

**Old version without observations import:**

You can still use the app, just need to enter observations manually through Quick Entry Log. OR wait for the code update to be deployed.

**Alternative:** Use "Load Sample Data" button to get generic sample data, then manually adjust students if needed.

---

**See STUDENT_PROFILES.md for detailed explanation of each student's patterns!**
