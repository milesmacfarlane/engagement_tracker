# Troubleshooting Guide

## Common Issues and Solutions

### Issue 1: Date Format Error

**Error Message:**
```
ValueError: time data "2026-02-04" doesn't match format "%Y-%m-%d %H:%M:%S"
```

**Cause:**
Mixed date formats in the observations.csv file (some dates with time, some without)

**Solution 1: Run the Fix Script**
```bash
python fix_dates.py
```

This will:
- Backup your existing data
- Convert all dates to consistent YYYY-MM-DD format
- Save the fixed file

**Solution 2: Manual Fix**
If you have the error and fix_dates.py doesn't work:

1. Navigate to the `data` folder
2. Open `observations.csv` in Excel or a text editor
3. Look at the `date` column
4. If dates look like `2026-02-04 00:00:00`, change them to `2026-02-04`
5. Save the file
6. Restart the app

**Solution 3: Delete and Reload**
If you're okay losing current data:
```bash
# Delete the data folder
rm -rf data/

# Restart the app
streamlit run app.py

# Load sample data in Setup → Data Management
```

---

### Issue 2: App Won't Start

**Error Message:**
```
ModuleNotFoundError: No module named 'streamlit'
```

**Solution:**
Install dependencies:
```bash
pip install -r requirements.txt
```

Or on Windows if you get permission errors:
```bash
pip install -r requirements.txt --user
```

---

### Issue 3: Observations Not Saving

**Symptoms:**
- Click "Save Observations"
- Get success message
- Data doesn't appear on dashboards

**Solution:**
Check these things:

1. **Verify data folder exists:**
   ```bash
   # Should see: data/students.csv, data/classes.csv, data/observations.csv
   ls data/
   ```

2. **Check file permissions:**
   - Make sure you have write access to the `data` folder
   - On Windows: Right-click folder → Properties → Security
   - On Linux/Mac: `chmod -R 755 data/`

3. **Verify observations.csv has content:**
   - Open `data/observations.csv` in Excel
   - Should see rows with your observations
   - If empty, try saving again

---

### Issue 4: Auto-Tab Not Working in Quick Entry

**Symptoms:**
- Typing in measure fields
- Doesn't auto-advance to next field

**Cause:**
Browser JavaScript may be disabled or conflicting extension

**Solution:**

1. **Try a different browser:**
   - Chrome, Firefox, or Edge (recommended)
   - Disable browser extensions temporarily

2. **Use Tab key manually:**
   - Type value
   - Press Tab
   - Continue to next field

3. **Use Enter for column navigation:**
   - Still faster than clicking!

---

### Issue 5: PDF Generation Fails

**Error Message:**
```
ModuleNotFoundError: No module named 'reportlab'
```

**Solution:**
Install reportlab:
```bash
pip install reportlab
```

Or reinstall all requirements:
```bash
pip install -r requirements.txt
```

---

### Issue 6: Student Not Appearing in Entry Log

**Symptoms:**
- Student exists in roster
- Doesn't show up in Quick Entry Log when class selected

**Solution:**

1. **Check student's primary class:**
   - Go to Setup → Student Roster
   - Find the student
   - Verify "Primary Class" matches the class you selected

2. **Edit if needed:**
   - Select the student in Setup
   - Update their Primary Class
   - Go back to Quick Entry Log
   - Student should now appear

---

### Issue 7: "No Data" in Dashboards

**Symptoms:**
- Observations were saved
- Dashboard shows "No observations recorded"

**Solutions:**

1. **Check date range:**
   - If using date filters, verify the range includes your observations
   - Try "All Observations" date range

2. **Verify correct student/class selected:**
   - Double-check dropdown selections
   - Make sure you're looking at the right student/class

3. **Check the data file:**
   - Open `data/observations.csv`
   - Verify your observations are there
   - Check student_id matches what's in students.csv

---

### Issue 8: Performance is Slow

**Symptoms:**
- App takes long to load
- Dashboards lag
- Entry log is slow

**Solutions:**

1. **Clear browser cache:**
   - Ctrl+Shift+Delete (Chrome/Edge)
   - Clear cached images and files

2. **Restart the app:**
   ```bash
   # Stop: Ctrl+C
   # Restart:
   streamlit run app.py
   ```

3. **Check data size:**
   - If you have 10,000+ observations, performance may degrade
   - Consider archiving old data
   - Export old observations and start fresh

---

### Issue 9: CSV Import Fails

**Error Message:**
```
CSV must contain columns: student_id, name, primary_class
```

**Solution:**

1. **Check your CSV file has exact column names:**
   - `student_id` (not StudentID or Student_ID)
   - `name` (not Name or Student Name)
   - `primary_class` (not Primary_Class or Class)

2. **Use the correct format:**
   ```csv
   student_id,name,primary_class
   100001,John Smith,HIS20A
   100002,Jane Doe,HIS20A
   ```

3. **Check for:**
   - No extra spaces in column names
   - No missing commas
   - Consistent quote usage

---

### Issue 10: Can't Delete a Class

**Symptoms:**
- Try to delete a class
- Nothing happens or error occurs

**Solution:**

1. **Students are assigned to that class:**
   - Go to Setup → Student Roster
   - Find all students in that class
   - Either:
     - Delete those students, OR
     - Change their Primary Class to a different class

2. **Then delete the class:**
   - Go to Setup → Classes
   - Select the class
   - Click Delete

---

## Getting More Help

### Check These First:
1. ✅ Read the error message carefully
2. ✅ Check this troubleshooting guide
3. ✅ Try restarting the app
4. ✅ Check the README.md for documentation
5. ✅ Review UPDATES.md for recent changes

### Debug Mode:
To see detailed error messages:
```bash
streamlit run app.py --logger.level=debug
```

### Test System Integrity:
```bash
python test_system.py
```

Should show:
```
ALL TESTS PASSED! ✅
```

### Test PDF Generation:
```bash
python test_pdf.py
```

Should show:
```
ALL PDF TESTS PASSED! ✅
```

---

## Quick Fixes Summary

| Issue | Quick Fix |
|-------|-----------|
| Date format error | `python fix_dates.py` |
| Missing modules | `pip install -r requirements.txt` |
| Auto-tab not working | Use Tab key manually or Enter for columns |
| Student not showing | Check Primary Class in Setup |
| No data in dashboard | Verify date range and selections |
| Slow performance | Restart app, clear browser cache |
| CSV import fails | Check column names exactly |
| Can't delete class | Reassign or delete students first |

---

## File Recovery

### Backup Your Data:
```bash
# Copy data folder
cp -r data/ data_backup/

# Or export from Setup → Data Management
```

### Restore from Backup:
```bash
# Copy backup back
cp -r data_backup/* data/

# Restart app
```

---

## Prevention Tips

1. ✅ **Export data regularly** (Setup → Data Management)
2. ✅ **Keep backups** before major changes
3. ✅ **Test with sample data** first
4. ✅ **Update regularly** (`pip install -r requirements.txt`)
5. ✅ **Use consistent date formats** (YYYY-MM-DD)
6. ✅ **Validate CSV files** before importing

---

## Still Having Issues?

If none of these solutions work:

1. **Check the error message** - often tells you exactly what's wrong
2. **Look at the data files** - open CSVs in Excel to inspect
3. **Try with fresh sample data** - helps identify if it's data or code issue
4. **Check Python version** - requires Python 3.8+
5. **Review file permissions** - make sure data folder is writable

---

## Version Information

To check what you're running:
```bash
python --version      # Should be 3.8+
streamlit --version   # Should be 1.28+
pip list | grep reportlab   # Should show 4.0+
```

---

**Last Updated:** 2024  
**Applies to:** Version 1.1
