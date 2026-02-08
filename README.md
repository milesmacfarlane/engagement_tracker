# Student Engagement Tracking System

A comprehensive web-based application for tracking and analyzing student behavioral engagement in classroom settings. Built with Python and Streamlit, this system allows educators to systematically observe, record, and analyze student engagement across 9 key behavioral measures.

## 📋 Features

### Core Functionality
- **Quick Entry Log**: Streamlined keyboard-friendly interface for recording daily observations
  - PRESENT/ABSENT radio buttons for quick attendance marking
  - Text input fields with auto-tab after typing
  - Enter key navigation down columns
  - Automatic "-" fill for absent students
- **Student Dashboard**: Detailed individual student performance reports with auto-generated insights
- **Class Dashboard**: Class-wide analytics and performance summaries
- **Reports**: Professional PDF report generation
  - Student reports (one-page summary with all statistics)
  - Class reports (supports single or multiple classes)
  - Date range filtering (All, Most Recent, Custom Range)
  - Greyscale-friendly for printing
- **Setup & Configuration**: Easy management of students, classes, and data

### Key Capabilities
- Track 9 behavioral engagement measures using a 1/0/- observation system
- Automatic performance calculation and band classification
- Visual analytics with interactive charts
- Auto-generated strengths and improvement areas
- Recommended next steps based on performance
- Professional PDF reports for documentation
- CSV import/export for data portability
- Sample data for demonstration

## 🎯 The Observation System

### The 9 Engagement Measures
1. **Time on Task** - Student stays focused on assigned work
2. **Asked/Answered/Shared** - Active participation in discussions
3. **Work Completed/Ready** - Assignments completed and prepared
4. **Materials/Organized** - Has necessary materials and workspace organized
5. **Helping/Asking for Help** - Seeks or provides assistance appropriately
6. **Asks for Clarification** - Seeks understanding when confused
7. **Check-ins with Teacher** - Regular communication with teacher
8. **Asks for Ways to Improve** - Seeks feedback and growth opportunities
9. **In-class Work Completed** - Completes work during class time

### Value System
- **1** = Behavior was observed/demonstrated
- **0** = Behavior was NOT observed (student present but behavior absent)
- **-** = Student was absent or measure not applicable

### Performance Calculation
```
Performance % = (Count of 1s) / (Count of 1s + Count of 0s) × 100
```
Note: Absences (-) are excluded from the denominator

### Performance Bands
- **85-100%**: Exemplary
- **75-85%**: Proficient
- **65-75%**: Developing
- **50-65%**: Emerging
- **40-50%**: Beginning
- **<40%**: Needs Intensive Support

## 🚀 Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Setup Steps

1. **Clone or download the repository**
   ```bash
   cd engagement_tracker
   ```

2. **Install required packages**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   streamlit run app.py
   ```

4. **Access the application**
   - The app will automatically open in your default browser
   - Default URL: `http://localhost:8501`

## 📖 Usage Guide

### First-Time Setup

1. **Option A: Load Sample Data** (Recommended for first-time users)
   - Navigate to "Setup" → "Data Management" tab
   - Click "Load Sample Data"
   - Explore the system with pre-populated data

2. **Option B: Manual Setup**
   - Navigate to "Setup" → "Classes" tab
   - Add your classes (e.g., "HIS20A - History 20 Section A")
   - Navigate to "Student Roster" tab
   - Add students individually or import from CSV

### Recording Observations

1. Navigate to "Quick Entry Log"
2. Select observation date and class
3. For each student, enter:
   - `1` for observed behaviors
   - `0` for behaviors not observed
   - `-` if student was absent
4. Click "Save Observations"

### Viewing Reports

**Individual Student Report:**
1. Navigate to "Student Dashboard"
2. Select class and student
3. Review:
   - Overall performance and band
   - Measure-by-measure breakdown
   - Top strengths and focus areas
   - Recommended next steps

**Class Report:**
1. Navigate to "Class Dashboard"
2. Select class
3. Review:
   - Class summary statistics
   - Performance distribution
   - Individual student table
   - Top and bottom performers
   - Observation priorities

### Data Management

**Export Data:**
- Navigate to "Setup" → "Data Management"
- Download students, classes, or observations as CSV

**Import Students:**
- Prepare CSV with columns: `student_id`, `name`, `primary_class`
- Navigate to "Setup" → "Student Roster" → "Bulk Import"
- Upload CSV file

**Backup Data:**
- Regularly export all data (students, classes, observations)
- Store CSV files in a safe location

## 📁 File Structure

```
engagement_tracker/
├── app.py                      # Main application entry point
├── database.py                 # Data persistence layer
├── utils.py                    # Calculation and utility functions
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── pages/
│   ├── entry_log.py           # Quick Entry Log page
│   ├── student_dashboard.py   # Student Dashboard page
│   ├── class_dashboard.py     # Class Dashboard page
│   └── setup.py               # Setup & Configuration page
└── data/                      # Data storage (auto-created)
    ├── students.csv           # Student roster
    ├── classes.csv            # Class list
    └── observations.csv       # Observation records
```

## 💾 Data Storage

The application uses CSV files for data persistence, stored in the `data/` directory:

- **students.csv**: Student roster (student_id, name, primary_class)
- **classes.csv**: Class list (class_code, class_name)
- **observations.csv**: All observation records (date, class_code, student_id, measure_name, value)

### Data Portability
CSV files can be:
- Opened in Excel or Google Sheets
- Backed up to cloud storage
- Transferred between computers
- Version controlled with Git

## 🔧 Troubleshooting

### Common Issues

**Students not appearing in entry log**
- Solution: Verify students are assigned to the correct class in Setup → Student Roster

**Performance shows as "N/A"**
- Solution: Ensure at least one observation with value 1 or 0 (not all absences)
- Check that valid observations exist (1s + 0s > 0)

**Cannot delete a class**
- Solution: First reassign or delete all students in that class

**Data not saving**
- Solution: Check that the `data/` directory exists and is writable
- Ensure you're clicking "Save Observations" button

**Application won't start**
- Solution: Verify all dependencies are installed: `pip install -r requirements.txt`
- Check Python version: `python --version` (should be 3.8+)

### Performance Issues

For large datasets (1000+ students or 10,000+ observations):
- Consider upgrading to PostgreSQL database
- Implement pagination in student lists
- Add date range filters for observations

## 🎨 Customization

### Modifying Performance Bands
Edit `utils.py` → `PERFORMANCE_BANDS` tuple:
```python
PERFORMANCE_BANDS = [
    (85, 100, "Exemplary", "#00B050"),
    # Add or modify bands here
]
```

### Adding New Measures
Edit `utils.py` → `ENGAGEMENT_MEASURES` list:
```python
ENGAGEMENT_MEASURES = [
    "Time on Task",
    # Add new measures here
]
```

### Changing Color Scheme
Edit `utils.py` → `COLORS` dictionary:
```python
COLORS = {
    'primary': '#1F4788',  # Change colors here
    # ...
}
```

## 📊 Sample Data

The system includes sample data generator with:
- 3 classes (HIS20A, HIS20B, SST20)
- 60-70 students (20-25 per class)
- 10 observation sessions
- Realistic performance patterns:
  - High performers (~85% behaviors observed)
  - Medium performers (~70% behaviors observed)
  - Lower performers (~40% behaviors observed)
  - Occasional absences

## 🔐 Security Notes

- No authentication is implemented by default
- Data is stored locally in CSV files
- For multi-user deployments, consider:
  - Adding user authentication
  - Using a proper database (PostgreSQL)
  - Implementing role-based access control
  - Deploying behind a firewall

## 🚀 Deployment

### Local Network Deployment
Run with network access:
```bash
streamlit run app.py --server.address 0.0.0.0
```

### Cloud Deployment
Can be deployed to:
- Streamlit Cloud (free tier available)
- Heroku
- AWS/Azure/GCP
- Any platform supporting Python web apps

## 📈 Future Enhancements

Potential additions:
- PDF report generation
- Email notifications for students needing attention
- Attendance tracking integration
- Mobile app for field observations
- Multi-language support
- Trend analysis and predictive analytics
- Parent portal access

## 🤝 Contributing

To contribute:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is provided as-is for educational purposes.

## 🙏 Acknowledgments

Built for educators who want to systematically track and improve student engagement in their classrooms.

## 📞 Support

For questions or issues:
- Check the Help section in the app (Setup → Help tab)
- Review this README
- Contact your system administrator

---

**Version:** 1.0  
**Last Updated:** 2024  
**Built with:** Python, Streamlit, Pandas, Plotly
