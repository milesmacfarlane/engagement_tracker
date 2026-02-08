# Quick Start Guide

## Get Up and Running in 5 Minutes

### Step 1: Installation (2 minutes)

```bash
# Navigate to the project directory
cd engagement_tracker

# Install required packages
pip install -r requirements.txt
```

### Step 2: Launch the App (30 seconds)

**Option A - Using the launch script:**
```bash
./launch.sh
```

**Option B - Direct launch:**
```bash
streamlit run app.py
```

The app will automatically open in your browser at `http://localhost:8501`

### Step 3: Load Sample Data (30 seconds)

1. Click on "⚙️ Setup" in the sidebar
2. Go to the "Data Management" tab
3. Click "🎲 Load Sample Data"
4. Done! The system is now populated with sample students and observations

### Step 4: Explore the Features (2 minutes)

#### Record an Observation
1. Navigate to "📝 Quick Entry Log"
2. Select a date and class
3. Enter 1, 0, or - for each student's behaviors
4. Click "💾 Save Observations"

#### View Student Report
1. Navigate to "👤 Student Dashboard"
2. Select a student from the dropdown
3. Review their performance, strengths, and focus areas

#### View Class Summary
1. Navigate to "📚 Class Dashboard"
2. Select a class
3. Review class-wide statistics and student rankings

## Using Your Own Data

### Add Your Classes
1. Go to Setup → Classes tab
2. Add each of your classes (e.g., "MATH101", "Mathematics 10-1")

### Add Your Students

**Option A - Manual Entry:**
1. Go to Setup → Student Roster tab
2. Fill in student ID, name, and primary class
3. Click "Add Student"

**Option B - Bulk Import:**
1. Create a CSV file with columns: `student_id`, `name`, `primary_class`
2. Go to Setup → Student Roster → Bulk Import
3. Upload your CSV file

## Tips for Success

✅ **Observe regularly** - Aim for at least once per week per student
✅ **Be consistent** - Use the same criteria across all observations  
✅ **Use all three values** - Don't default to one value for everything
✅ **Review dashboards** - Check student and class dashboards weekly
✅ **Export data** - Back up your observations regularly

## Common Workflows

### Daily Observation Workflow
1. Open Quick Entry Log
2. Select today's date
3. Select first class
4. Observe students and enter values
5. Save observations
6. Repeat for other classes

### Weekly Review Workflow
1. Open Class Dashboard
2. Review class performance distribution
3. Note students who are overdue for observation
4. Check top/bottom performers
5. Open Student Dashboard for students needing attention
6. Review their focus areas and recommended next steps

### Monthly Reporting Workflow
1. Open Class Dashboard for each class
2. Download performance summary as CSV
3. Open Student Dashboard for struggling students
4. Export detailed reports
5. Use data for RTI/parent meetings

## Keyboard Shortcuts

When in the Streamlit app:
- Press `R` to rerun the app
- Press `C` to clear cache
- Press `?` for help menu

## Getting Help

- Check the Help tab in Setup for detailed documentation
- Review the README.md for comprehensive information
- Run `python test_system.py` to verify system integrity

## Next Steps

Once comfortable with the basics:
- Customize performance bands in `utils.py`
- Add new engagement measures
- Adjust color schemes
- Export data for further analysis in Excel

---

**Ready to start tracking engagement systematically?**  
Launch the app and load sample data to explore all features!
