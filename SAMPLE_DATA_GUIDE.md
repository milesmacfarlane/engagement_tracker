# Custom Sample Data - Student Profiles

## Overview
This dataset contains 8 students with distinct behavioral profiles, observed over 20 weekdays in January 2026 (Jan 2-29, 2026) in class EMA40 - Essential Math (Grade 12, Period D).

## How to Load This Data

### Option 1: Automatic Generation
```bash
cd engagement_tracker
python generate_custom_data.py
streamlit run app.py
```

### Option 2: Manual Import
1. Launch the app
2. Go to Setup → Data Management
3. Import the CSV files from the `data/` folder

---

## Student Profiles

### 1️⃣ Student One (1111111)
**Profile:** Poor attender, rarely focused when they do attend

**Expected Behavior:**
- **Attendance Rate:** 40% (8 absences out of 20 days)
- **Performance When Present:** ~14% (Needs Intensive Support)
- **Characteristics:**
  - Rarely on task
  - Minimal participation
  - Often unprepared
  - Doesn't complete work

**Actual Results:**
- Attendance: 60% (12/20 days) 
- Performance: 13.9% - Needs Intensive Support
- Pattern: Frequent absences, very low engagement when present

---

### 2️⃣ Student Two (2222222)
**Profile:** Poor attender, wants to do well but is lost and underperforms

**Expected Behavior:**
- **Attendance Rate:** 45% (11 absences out of 20 days)
- **Performance When Present:** ~47% (Beginning)
- **Characteristics:**
  - Asks for help frequently
  - Wants clarification
  - Motivated to improve
  - Struggles to finish work despite effort

**Actual Results:**
- Attendance: 45% (9/20 days)
- Performance: 46.9% - Beginning
- Pattern: Poor attendance, but shows effort when present (asks questions, seeks help)

---

### 3️⃣ Student Three (3333333)
**Profile:** Moderate attender, floats by with prior knowledge, only marginally engaged

**Expected Behavior:**
- **Attendance Rate:** 70% (6 absences out of 20 days)
- **Performance When Present:** ~46% (Beginning)
- **Characteristics:**
  - Completes work using prior knowledge
  - Doesn't ask many questions
  - Not motivated to go beyond minimum
  - Coasting attitude

**Actual Results:**
- Attendance: 60% (12/20 days)
- Performance: 46.3% - Beginning
- Pattern: Moderate attendance, relies on prior knowledge, minimal engagement

---

### 4️⃣ Student Four (4444444)
**Profile:** Moderate attender, does well in class and helps others but always anxious and feels behind

**Expected Behavior:**
- **Attendance Rate:** 70% (6 absences out of 20 days)
- **Performance When Present:** ~77% (Proficient)
- **Characteristics:**
  - Very organized
  - Helps classmates frequently
  - Checks in with teacher often (anxiety)
  - Asks many clarifying questions
  - Wants to improve

**Actual Results:**
- Attendance: 75% (15/20 days)
- Performance: 77.0% - Proficient
- Pattern: Solid performance, high helping behavior, frequent check-ins

---

### 5️⃣ Student Five (5555555)
**Profile:** Good attender but rarely focused when they do attend

**Expected Behavior:**
- **Attendance Rate:** 90% (2 absences out of 20 days)
- **Performance When Present:** ~23% (Needs Intensive Support)
- **Characteristics:**
  - Present physically but not mentally
  - Low time on task
  - Doesn't participate much
  - Work incomplete

**Actual Results:**
- Attendance: 85% (17/20 days)
- Performance: 22.9% - Needs Intensive Support
- Pattern: Excellent attendance, but very poor engagement (body present, mind elsewhere)

---

### 6️⃣ Student Six (6666666)
**Profile:** Good attender, floats by with prior knowledge, only marginally engaged

**Expected Behavior:**
- **Attendance Rate:** 90% (2 absences out of 20 days)
- **Performance When Present:** ~53% (Emerging)
- **Characteristics:**
  - Completes work adequately
  - Uses prior knowledge
  - Doesn't seek improvement
  - Goes through the motions

**Actual Results:**
- Attendance: 90% (18/20 days)
- Performance: 53.1% - Emerging
- Pattern: Consistent attendance, moderate engagement, coasting on prior knowledge

---

### 7️⃣ Student Seven (7777777)
**Profile:** Good attender, does well in class

**Expected Behavior:**
- **Attendance Rate:** 95% (1 absence out of 20 days)
- **Performance When Present:** ~84% (Exemplary)
- **Characteristics:**
  - Highly engaged
  - Completes all work
  - Participates actively
  - Organized and prepared

**Actual Results:**
- Attendance: 85% (17/20 days)
- Performance: 83.7% - Proficient
- Pattern: Strong attendance and engagement across all measures

---

### 8️⃣ Student Eight (8888888)
**Profile:** Good attender, does well but only the minimum, finishes quickly then wastes time

**Expected Behavior:**
- **Attendance Rate:** 90% (2 absences out of 20 days)
- **Performance When Present:** ~61% (Emerging)
- **Characteristics:**
  - Finishes work quickly
  - Does minimum required
  - Time on task drops after completion
  - Capable but not motivated

**Actual Results:**
- Attendance: 90% (18/20 days)
- Performance: 61.1% - Emerging
- Pattern: Good attendance, completes work efficiently, then disengages

---

## Performance Summary Table

| Student | Attendance | Performance | Band | Key Characteristic |
|---------|-----------|-------------|------|-------------------|
| 1111111 | 60% | 13.9% | Needs Intensive Support | Poor attendance + unfocused |
| 2222222 | 45% | 46.9% | Beginning | Poor attendance + struggling |
| 3333333 | 60% | 46.3% | Beginning | Moderate attendance + coasting |
| 4444444 | 75% | 77.0% | Proficient | Anxious helper |
| 5555555 | 85% | 22.9% | Needs Intensive Support | Present but unfocused |
| 6666666 | 90% | 53.1% | Emerging | Good attendance + coasting |
| 7777777 | 85% | 83.7% | Proficient | Engaged high performer |
| 8888888 | 90% | 61.1% | Emerging | Minimalist worker |

---

## Measure-by-Measure Patterns

### Students with Distinctive Measure Patterns:

**Student 2 (Struggling but Trying):**
- HIGH: Asks for Clarification (70%), Helping/Asking for Help (60%)
- LOW: In-class Work Completed (25%)
- Shows effort to understand but struggles with execution

**Student 4 (Anxious Helper):**
- HIGH: Helping/Asking for Help (90%), Check-ins with Teacher (85%), Materials/Organized (85%)
- Helping behavior is dominant trait

**Student 5 (Present but Unfocused):**
- LOW across all measures despite high attendance
- Physical presence doesn't translate to engagement

**Student 8 (Efficient Minimalist):**
- HIGH: Work Completed/Ready (80%), In-class Work Completed (75%)
- MODERATE: Time on Task (60%) - drops after finishing
- Does the work efficiently but doesn't go beyond

---

## Use Cases for This Data

### Teaching Scenarios:
1. **Identify intervention priorities** - Students 1 and 5 need immediate attention
2. **Differentiate support strategies** - Student 2 needs skill-building, Student 5 needs engagement strategies
3. **Recognize helping behavior** - Student 4 could be a peer tutor
4. **Address underachievement** - Students 3, 6, 8 are capable but unmotivated

### Dashboard Practice:
1. **Class Dashboard** - See distribution across performance bands
2. **Student Dashboard** - Compare profiles (e.g., Student 1 vs Student 5 - both low performance, different causes)
3. **Reports** - Generate PDFs showing different student needs

### Data Analysis:
1. **Attendance vs Performance** - Note that attendance alone doesn't guarantee engagement (Student 5)
2. **Engagement Patterns** - Identify which measures predict success
3. **Intervention Tracking** - Use baseline data to measure improvement over time

---

## Observation Dates

**20 Weekdays in January 2026:**
- Week 1: Jan 2 (Fri)
- Week 2: Jan 5-9 (Mon-Fri)
- Week 3: Jan 12-16 (Mon-Fri)
- Week 4: Jan 19-23 (Mon-Fri)
- Week 5: Jan 26-29 (Mon-Thu)

Total: 20 school days
Total observations: 1,440 (8 students × 20 days × 9 measures)

---

## Technical Details

### Data Generation:
- Attendance determined probabilistically based on profile
- Engagement measures vary by ±15% from baseline to add realism
- Values: '1' (observed), '0' (not observed), '-' (absent)
- All dates in ISO format (YYYY-MM-DD)

### File Structure:
```
data/
├── students.csv        # 8 students
├── classes.csv         # 1 class (EMA40)
└── observations.csv    # 1,440 observations
```

---

## Expected Dashboard Views

### Class Dashboard Should Show:
- Class Average: ~50-55%
- Distribution: 2 Needs Support, 2 Beginning, 2 Emerging, 2 Proficient
- Students needing attention: 1111111, 5555555 (both very low despite different reasons)

### Individual Dashboards Should Reveal:
- **Student 1:** Attendance + engagement issues
- **Student 2:** Attendance + skill issues
- **Student 4:** High performer with anxiety patterns (high check-ins)
- **Student 5:** Attendance ≠ engagement disconnect

---

## Regenerating Data

To generate a new random sample with the same profiles:
```bash
python generate_custom_data.py
```

Each run will produce different random variations while maintaining the core behavior patterns.

---

**Created:** February 2026  
**Purpose:** Realistic sample data for training and demonstration  
**Students:** 8 with distinct profiles  
**Timeframe:** January 2-29, 2026 (20 weekdays)
