# Student Engagement Tracker - Setup Workflow

## Getting Started

Follow this workflow to set up your system and start recording observations:

### Step 1: Create Classes
**Location:** Sidebar → Classes

1. Click **"Classes"** in the sidebar
2. Click **"Create First Class"** or **"Add Class"**
3. Enter:
   - **Class Code**: Short identifier (e.g., `HistoryA`, `BioB`)
   - **Class Name**: Full name (e.g., `History 20 Section A`)
4. Click **"Create"**
5. Repeat for each class

**Next Step:** When classes are created, click **"Next: Add Students →"**

---

### Step 2: Add Students
**Location:** Sidebar → Students

#### Option A: Add Students One by One
1. Click **"Students"** in the sidebar
2. Click **"Add Student"**
3. Enter:
   - **Student ID**: Student number/ID
   - **Name**: First and last name
   - **Class**: Select from dropdown
4. Click **"Create"**
5. Repeat for each student

#### Option B: Import from CSV (Faster)
1. Click **"Students"** in the sidebar
2. Click **"Import CSV"**
3. Select your CSV file with format:
   ```
   student_id,name,primary_class
   1001,John Doe,HistoryA
   1002,Jane Smith,HistoryA
   ```
4. Click **"Import"**

**Next Step:** When students are added, click **"Next: Record Observations →"**

---

### Step 3: Record Observations
**Location:** Sidebar → Quick Entry Log

1. Click **"Quick Entry Log"** in the sidebar
2. Select **observation date** and **class**
3. Grid appears with students and measures
4. For each cell, enter:
   - `1` = Behavior observed
   - `0` = Behavior not observed
   - `-` = Student absent or N/A
5. Use keyboard shortcuts:
   - Arrow keys to navigate
   - Tab/Shift+Tab to move between cells
   - Enter to save and move down
6. Use batch actions:
   - **"Absent"** = Mark all behaviors as 0 for a student
   - **"Clear"** = Clear a student's row
   - **"Clear All"** = Reset entire grid
7. Click **"Save Observations"** when complete

---

### Step 4: View Reports & Analytics
**Location:** Sidebar → Dashboard, Students, Classes, Reports

- **Dashboard**: Overview of all classes and quick stats
- **Students**: View student performance metrics
- **Classes**: See class-wide performance
- **Reports**: Generate PDF reports (coming soon)

---

## CSV Import Format

Create a CSV file with headers and data:

```csv
student_id,name,primary_class
1000,AMIN FAISAL,HistoryA
1001,ARCENA IAN KIEL,HistoryA
1002,BLAICH KAYDANCE,HistoryB
1003,BYLE DOMINIK,SocialStudies
```

**Requirements:**
- Exact column names: `student_id`, `name`, `primary_class`
- Class codes must exist already
- Student IDs must be unique
- No duplicate entries will be imported

---

## Tips for Success

### Classes Setup
- Use consistent class codes (e.g., `HistoryA`, `HistoryB`, `SocialStudies`)
- Code should match what's in your student CSV file
- You can edit or delete classes if needed (as long as no students are assigned)

### Student Import
- Prepare CSV with student number, full name, and course code
- Name format: `LAST NAME, FIRST NAME` or `FIRST LAST` both work
- All students must be assigned to an existing class
- One class code per student

### Recording Observations
- Start with 5 key measures for tracking
- Use keyboard shortcuts to speed up entry:
  - Quick keys: `1`, `0`, `-` for immediate entry
  - Navigate with arrow keys for efficiency
  - Batch "Absent" button for students not present
  
### Data Quality
- Make observations on the same day for consistency
- Limit observations to 5-10 behaviors per class per day
- Regular (weekly) observations give better performance trends
- Clear absent markers (`-`) help calculate accurate performance %

---

## Navigation

All pages have:
- **Breadcrumb navigation** at top (Dashboard → Current Page)
- **Sidebar menu** for main navigation (collapsible)
- **"Next Step" buttons** to guide workflow
- **Back links** to return to related pages

If you get stuck, use the sidebar to navigate back to Dashboard.

---

## Troubleshooting

### "Failed to load data"
→ Check browser console (F12) for error message
→ Ensure backend is running (`uvicorn app.main:app --reload`)
→ Check database connection

### Import showing "Class not found"
→ Go to Classes page and verify class codes match CSV exactly
→ Class codes are case-sensitive: `HistoryA` ≠ `historya`

### Students not appearing in Entry Log
→ Go to Classes page, verify students are assigned to the selected class
→ Go to Students page and check the class assignment

---

**Current Version:** 2.0 (Next.js + FastAPI)  
**Last Updated:** September 2026
