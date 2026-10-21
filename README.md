# 🎓 Intelligent Study Assistant Website

An AI-powered academic study platform built with **Python**, **Streamlit**, and **Google Gemini** (with built-in offline NLP fallback).

Designed to transform raw lecture notes, textbooks, and research papers into high-retention active-learning materials: automated summaries, interactive mind maps, spaced repetition flashcard decks, exam simulators, conversational AI tutors, and custom study plans.

---

## 🌟 Key Features

### 1. 📑 Smart Summaries & Visual Mind Maps
- **Multi-tiered Summarization**: Instant TL;DR, comprehensive executive summary, and bullet-point cheat sheets.
- **Key Definitions Extractor**: Automatically extracts and catalogs critical domain terminology.
- **Visual Concept Mind Maps**: Generates interactive Mermaid.js hierarchy charts connecting foundational concepts to advanced principles.

### 2. 🗂️ Interactive Flashcards & Leitner Spaced Repetition (SRS)
- **Active Recall Decks**: Auto-generates high-yield Q&A cards from your notes.
- **Leitner 3-Box System**: Categorizes cards into *Learning (Box 1)*, *Review (Box 2)*, and *Mastered (Box 3)* based on user recall feedback (*Hard*, *Good*, *Easy*).
- **Import & Export**: Export decks as JSON or Anki-compatible CSV; import pre-made decks.

### 3. 📝 AI Practice Quiz & Exam Simulator
- **Diverse Question Types**: High-order Multiple Choice Questions (MCQ) and True/False assertions.
- **Customizable Difficulty**: Tailor tests for High School, College/Intermediate, or Graduate levels.
- **Instant Grading & Explanations**: Calculates score percentages and letter grades, paired with conceptual rationales explaining correct and incorrect options.

### 4. 💬 "Ask My Notes" AI Tutor
- **Pedagogical Personas**:
  - **Feynman Technique Mode**: Explains intricate topics using intuitive, real-world analogies suitable for a 10-year-old.
  - **Socratic Mentor**: Guides students through probing questions rather than passive spoon-feeding.
  - **Exam Prep Coach**: Focuses on memory mnemonics, exam traps, and scoring tips.
  - **Academic Tutor**: Formal, structured scholarly explanations.
- **Document-Grounded**: Answers are anchored in your uploaded document text.

### 5. ⏱️ Study Planner & Focus Pomodoro
- **Spaced Repetition Timetable**: Generates day-by-day study schedules based on exam date, daily hours, and intensity style.
- **Built-in Pomodoro Station**: 25/5 and 50/10 focus intervals with audio cues.
- **Ambient Focus Audio**: Synthesized calming brown noise generator for distraction-free immersion.

### 6. 📊 Progress Analytics & Study Pack Export
- **Visual Analytics**: Interactive Plotly donut charts for flashcard mastery and score trajectory graphs.
- **One-Click Study Pack Download**: Export complete summary, glossary, flashcard deck, and quiz as a unified Markdown document.

---

## 🚀 Quick Start Guide

### 1. Requirements
- Python 3.10+ installed
- Dependencies in `requirements.txt`:
  ```bash
  pip install -r requirements.txt
  ```

### 2. Launch the Application
- **Option A (Double-click)**: Run `run.bat` in the project root folder.
- **Option B (Command Line)**:
  ```bash
  cd "c:\Users\lnvpr\OneDrive\Desktop\Intelligent_study_Assistant"
  python -m streamlit run app.py
  ```

### 3. AI Mode Configuration
- **Gemini Online Mode (Recommended)**: Enter your free Gemini API key from [Google AI Studio](https://aistudio.google.com) in the left sidebar.
- **Intelligent Heuristic Mode**: Works 100% offline out-of-the-box without any API key required!

---

## 📁 Project Architecture

```
Intelligent_study_Assistant/
│
├── app.py                     # Main Streamlit web application & UI orchestrator
├── run.bat                    # One-click Windows startup script
├── requirements.txt           # Project dependencies
├── README.md                  # System documentation
│
├── modules/
│   ├── __init__.py
│   ├── document_processor.py  # PDF, DOCX, TXT parser & readability metrics
│   ├── ai_engine.py           # Gemini 2.5/1.5 client & Offline Heuristic Engine
│   ├── summarizer.py          # Multi-format summaries & Mermaid mindmaps
│   ├── flashcards.py          # Leitner spaced repetition flashcards & Anki CSV
│   ├── quiz_generator.py      # MCQ / True-False exam simulator & grading
│   ├── tutor_chat.py          # Conversational tutor with Feynman/Socratic modes
│   ├── study_planner.py       # Timetable generator & Pomodoro focus timer
│   └── analytics.py           # Progress charts & study pack export
│
└── assets/
    ├── styles.css             # Theme stylesheet (glassmorphism & badges)
    └── sample_notes.py        # Pre-loaded notes (AI/ML, Biology, History)
```
