# CampusAI: Intent Dataset Engineering

## 1. Dataset Overview
- **Dataset File:** `data/intent_dataset/intent_dataset.json`
- **Total Examples:** 689 validated examples
- **Active Intent Classes:** 13 balanced classes
- **Linguistic Distribution:**
  - English: 72.4%
  - Telugu Script (`te`): 14.8%
  - Romanized Telugu / Code-Mixed (`te-en`): 12.8%
- **Splits:**
  - Train Set: 551 examples (80%)
  - Test Set: 138 examples (20%) stratified by intent class

## 2. Dataset Generation Strategy
The dataset was produced using real entity grounding against actual course titles, department codes, and semester numbers extracted from the Aditya University curriculum PDFs:
1. **Template-Driven Grounding:** Real course names (`Operating Systems`, `Data Structures`, `Machine Learning`, `DBMS`, `Computer Networks`) paired with real department abbreviations.
2. **Linguistic Diversity:**
   - Formal queries: *"What is the prescribed credit allocation for Database Management Systems in Computer Science and Engineering?"*
   - Informal student questions: *"how many credits does dbms carry?"*
   - Typographical & casing variations: *"operating system unit 3 topics", "sem 5 subjects"*
   - Code-Mixed Telugu: *"CSE 3rd sem lo unna subjects list cheppandi"*
   - Telugu Script: *"ఆపరేటింగ్ సిస్టమ్స్ క్రెడిట్స్ ఎన్ని?"*
3. **Hard-Negative Pairs:**
   - *"What is the code of Data Structures?"* (`course_code`) vs *"What is the syllabus of Data Structures?"* (`full_syllabus`)
   - *"What subjects are offered in Semester 5?"* (`semester_subjects`) vs *"What topics are in Unit 5?"* (`unit_syllabus`)
