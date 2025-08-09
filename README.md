# StudySwift 
**An all-in-one intelligent tutoring and classroom management platform**  
Built with **Django (Python)**, **HTML**, **CSS**, and **JavaScript**

---

## Overview
**StudySwift** is a powerful web application designed to transform the learning experience for **students**, **teachers**, and **administrators**.  
From AI-assisted studying to class management, homework tracking, and secure messaging, StudySwift streamlines academic collaboration and makes learning smarter, faster, and more engaging.

---

## Key Features

### Login & Security
- Account types: **Student**, **Teacher**, **Administrator**
- Email verification upon registration
- Secure password rules (min. 8 chars, not common, not numeric-only)
- Password reset & recovery via email
- Logout functionality

### User-Friendly Interface
- Clean, elegant, and intuitive design
- Easy navigation via navbar
- Clear, readable labels and layouts

### Settings
- View and edit profile
- Upload/change profile picture
- View account credentials
- Password reset
- Sign out

### Calendar System
- Navigate months, jump to **today**
- Add and delete events
- Subject-based academic conference integration (via *AllConferenceAlert*)
- Color-coded events for clarity

### Messaging System
- Direct messages between class members
- Timestamped messages with inappropriate content filtering
- Edit/delete messages (within 3 hours)
- Clear chat history

---

## For Students

### Dashboard
- Welcome message & profile picture
- Pie chart for positive/negative points
- Rewards locker display
- Progress line chart for test results

### Homework Management
- Sections: Missing, Pending, Completed
- View assignments with details, files, and upload/download support
- Mark as completed

### Exams
- Take multiple-choice exams
- Auto-move to "Completed" after submission
- View scores

### Classrooms
- Join classes via 4-character code
- View class details & leaderboards

### Flashcards
- Create, delete, and revise flashcards
- Self-test mode with scoring
- Doughnut chart breakdown by subject

### Study Bot
- Subject-specific academic Q&A
- Rejects irrelevant or non-academic queries

### Rewards
- Points system with rewards store
- Purchase rewards using positive points
- Rewards locker with quantities

---

## For Teachers

### Dashboard
- Welcome message & profile picture
- Overview of classes and students

### Homework System
- Create, edit, delete assignments
- Upload/download files
- View student submissions

### Exams
- Create exams with questions, multiple-choice answers, and scoring
- View student submissions and incorrect answers

### Classrooms
- Same features as students + ability to:
  - Assign/remove points
  - View student progress via charts

---

## For Administrators

### Classroom Management
- Create/delete classes (auto-generate code)
- View all users & classrooms
- Remove students from classes
- Allocate teachers and students
- Enforce class changes for discipline

---

## Tech Stack
- **Backend:** Django (Python)
- **Frontend:** HTML, CSS, JavaScript
- **Database:** (Specify e.g. SQLite/PostgreSQL/MySQL)
- **Charts:** (Specify e.g. Chart.js / Plotly)
- **Email Services:** Django Email Backend (SMTP)

---

## Video Demonstration

https://drive.google.com/file/d/1jsarHEZ3pINsFZKv71zQTkz04vxA1HNF/view?usp=sharing
