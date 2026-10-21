"""
Study Planner and Pomodoro Focus Timer module.
Generates structured spaced-repetition schedules and provides a focus environment.
"""

import datetime
import math
from typing import List, Dict, Any
from .ai_engine import AIEngine


def generate_study_plan(
    topics: List[str],
    exam_date: datetime.date,
    daily_hours: float,
    intensity: str = "Balanced",
    ai_engine: AIEngine = None
) -> Dict[str, Any]:
    """Generate a personalized spaced-repetition study schedule leading up to exam date."""
    today = datetime.date.today()
    days_left = max(1, (exam_date - today).days)
    total_study_hours = round(days_left * daily_hours, 1)

    if not topics:
        topics = ["Core Concepts", "Deep Dive & Case Studies", "Practice Exams & Active Recall", "Final Synthesis"]

    # If AI engine is online, request tailored pedagogical schedule
    if ai_engine and ai_engine.is_ai_online:
        prompt = f"""You are an elite academic productivity strategist.
Create a high-impact, scientifically spaced study timetable.

Parameters:
- Today's Date: {today.strftime('%Y-%m-%d')}
- Exam Date: {exam_date.strftime('%Y-%m-%d')} ({days_left} days remaining)
- Available Daily Hours: {daily_hours} hrs/day (Total {total_study_hours} hrs)
- Intensity Level: {intensity}
- Topics to Master: {', '.join(topics)}

Provide a structured study plan including:
1. Phase Breakdown (Learning Phase, Active Recall Phase, Mock Exam Simulation Phase).
2. Recommended Daily Routine & Pomodoro distribution.
3. Milestones and Checkpoints.
4. Top 3 psychological retention strategies for this timeline.

Format cleanly with markdown headers, tables, and bullet points.
"""
        plan_text = ai_engine.generate_text(prompt)
        return {
            "days_left": days_left,
            "total_hours": total_study_hours,
            "daily_hours": daily_hours,
            "plan_markdown": plan_text,
            "schedule_table": _build_algorithmic_schedule(topics, days_left, daily_hours)
        }
    else:
        # Algorithmic structured schedule
        return {
            "days_left": days_left,
            "total_hours": total_study_hours,
            "daily_hours": daily_hours,
            "plan_markdown": _format_algorithmic_plan_markdown(topics, days_left, daily_hours, intensity),
            "schedule_table": _build_algorithmic_schedule(topics, days_left, daily_hours)
        }


def _build_algorithmic_schedule(topics: List[str], days_left: int, daily_hours: float) -> List[Dict[str, Any]]:
    """Build a day-by-day spaced repetition schedule table."""
    schedule = []
    today = datetime.date.today()
    num_topics = max(1, len(topics))
    
    # 60% days for first pass, 30% for active recall/revision, 10% for full mock exams
    learn_days = max(1, math.ceil(days_left * 0.6))
    review_days = max(1, math.ceil(days_left * 0.3))
    mock_days = max(1, days_left - learn_days - review_days)

    day_counter = 1
    # Phase 1: Deep Comprehension
    for i in range(learn_days):
        topic_idx = i % num_topics
        target_date = today + datetime.timedelta(days=i)
        schedule.append({
            "Day": f"Day {day_counter} ({target_date.strftime('%b %d')})",
            "Phase": "🧠 Deep Comprehension",
            "Focus Topic": topics[topic_idx],
            "Recommended Tasks": f"Read notes, create flashcards, complete 25-min Pomodoro drills ({daily_hours} hrs)",
            "Target Hours": daily_hours
        })
        day_counter += 1

    # Phase 2: Active Recall & Spaced Repetition
    for i in range(review_days):
        target_date = today + datetime.timedelta(days=day_counter - 1)
        schedule.append({
            "Day": f"Day {day_counter} ({target_date.strftime('%b %d')})",
            "Phase": "🔄 Active Recall Drills",
            "Focus Topic": f"Review Deck & Weak Spots ({topics[i % num_topics]})",
            "Recommended Tasks": f"Leitner flashcards practice, self-quiz without notes ({daily_hours} hrs)",
            "Target Hours": daily_hours
        })
        day_counter += 1

    # Phase 3: Mock Exam & Final Review
    for i in range(mock_days):
        target_date = today + datetime.timedelta(days=day_counter - 1)
        schedule.append({
            "Day": f"Day {day_counter} ({target_date.strftime('%b %d')})",
            "Phase": "🏆 Exam Simulation & Rest",
            "Focus Topic": "Full Comprehensive Simulation",
            "Recommended Tasks": f"Timed practice exam, error analysis, light review & sleep hygiene ({daily_hours} hrs)",
            "Target Hours": daily_hours
        })
        day_counter += 1

    return schedule[:min(days_left, 30)]


def _format_algorithmic_plan_markdown(topics: List[str], days_left: int, daily_hours: float, intensity: str) -> str:
    """Format markdown text report for algorithmic plan."""
    return f"""### 📅 High-Impact Study Roadmap ({intensity} Strategy)

- **Total Horizon**: {days_left} calendar days remaining
- **Daily Commitment**: {daily_hours} hours/day
- **Cumulative Study Budget**: {round(days_left * daily_hours, 1)} focused hours

---

#### 📌 Phase 1: Initial Ingestion & Active Note Condensation (Days 1 to {max(1, int(days_left * 0.6))})
- Break study material into 25-minute Pomodoro sprints.
- Convert raw readings into Flashcards immediately after each section.
- Avoid passive re-reading; test yourself on definitions within 2 hours.

#### 📌 Phase 2: Interleaved Retrieval Practice (Days {max(1, int(days_left * 0.6)) + 1} to {max(1, int(days_left * 0.9))})
- Shift 70% of study time to the **Practice Quiz & Exam Simulator**.
- Alternate between topics to stimulate neural consolidation (interleaving).
- Focus on Flashcards flagged as "Hard" in the Spaced Repetition deck.

#### 📌 Phase 3: Full Simulation & Peak Readiness (Final Days)
- Take full timed practice quizzes under closed-book exam conditions.
- Review cheat-sheet and executive summaries.
- Maintain consistent sleep schedule for cognitive consolidation.
"""
