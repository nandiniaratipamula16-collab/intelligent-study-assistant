"""
AI Practice Quiz and Exam Simulator with multiple question formats (MCQ, True/False),
instant grading, and comprehensive answer explanations.
"""

import json
import random
import re
from typing import List, Dict, Any, Optional
from .ai_engine import AIEngine


def generate_quiz(text: str, ai_engine: AIEngine, num_questions: int = 5, difficulty: str = "Medium") -> List[Dict[str, Any]]:
    """Generate quiz questions using Gemini or the built-in heuristic generator."""
    if not text.strip():
        return []

    if ai_engine.is_ai_online:
        return _generate_ai_quiz(text, ai_engine, num_questions, difficulty)
    else:
        return _generate_heuristic_quiz(text, ai_engine, num_questions)


def _generate_ai_quiz(text: str, ai_engine: AIEngine, num_questions: int, difficulty: str) -> List[Dict[str, Any]]:
    """Prompt Gemini to create realistic, high-order thinking exam questions."""
    prompt = f"""You are an expert exam designer and university professor.
Generate a high-yield study quiz based on the material below.

Difficulty Level: {difficulty}
Number of Questions: {num_questions}

Study Material:
\"\"\"{text[:9500]}\"\"\"

Generate exactly {num_questions} questions (include a mix of Multiple Choice and True/False).
Return a valid JSON array of objects with the exact schema:
[
  {{
    "id": 1,
    "type": "mcq",
    "question": "Question text here...",
    "options": ["A) ...", "B) ...", "C) ...", "D) ..."],
    "correct_answer": "A) ...",
    "explanation": "Detailed explanation of why this answer is correct and why other options are incorrect."
  }},
  {{
    "id": 2,
    "type": "true_false",
    "question": "Statement text here...",
    "options": ["True", "False"],
    "correct_answer": "True",
    "explanation": "Explanation of why the statement is factually true or false."
  }}
]

Respond ONLY with the JSON array.
"""
    try:
        raw_output = ai_engine.generate_text(prompt)
        clean = raw_output.strip()
        if clean.startswith("```json"):
            clean = clean[7:]
        if clean.startswith("```"):
            clean = clean[3:]
        if clean.endswith("```"):
            clean = clean[:-3]
        clean = clean.strip()
        
        quiz_data = json.loads(clean)
        for idx, q in enumerate(quiz_data):
            q["id"] = idx + 1
        return quiz_data[:num_questions]
    except Exception as e:
        return _generate_heuristic_quiz(text, ai_engine, num_questions)


def _generate_heuristic_quiz(text: str, ai_engine: AIEngine, num_questions: int) -> List[Dict[str, Any]]:
    """Generate rule-based quiz questions without requiring an API key."""
    quiz = []
    definitions = ai_engine.extract_key_definitions(text)
    keywords = [kw for kw, _ in ai_engine.extract_keywords(text, top_n=20)]
    
    # 1. Generate MCQs from definitions
    for d in definitions:
        correct_term = d["term"]
        other_terms = [other["term"] for other in definitions if other["term"] != correct_term]
        
        # Add keyword distractors if not enough definition terms
        for kw in keywords:
            if kw.capitalize() != correct_term and kw.capitalize() not in other_terms:
                other_terms.append(kw.capitalize())
                
        random.shuffle(other_terms)
        distractors = other_terms[:3]
        
        if len(distractors) < 3:
            distractors += [f"Concept {chr(65+i)}" for i in range(3 - len(distractors))]
            
        all_choices = [correct_term] + distractors[:3]
        random.shuffle(all_choices)
        
        labeled_options = [f"{chr(65+i)}) {choice}" for i, choice in enumerate(all_choices)]
        correct_labeled = next(opt for opt in labeled_options if correct_term in opt)
        
        quiz.append({
            "id": len(quiz) + 1,
            "type": "mcq",
            "question": f"Which term is defined as: \"{d['definition']}\"?",
            "options": labeled_options,
            "correct_answer": correct_labeled,
            "explanation": f"'{correct_term}' is explicitly defined in your notes as: {d['definition']}"
        })
        if len(quiz) >= num_questions:
            return quiz

    # 2. Generate True/False questions from clear sentences
    sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if 30 < len(s.strip()) < 150]
    for sent in sentences[:num_questions]:
        # Occasionally flip negation to create a False question
        is_true = random.choice([True, False])
        question_text = sent
        explanation = f"According to your study material: \"{sent}\""
        
        if not is_true and " is " in sent:
            question_text = sent.replace(" is ", " is never ")
            explanation = f"This statement is FALSE. The actual text states: \"{sent}\""
            
        quiz.append({
            "id": len(quiz) + 1,
            "type": "true_false",
            "question": f"True or False: {question_text}",
            "options": ["True", "False"],
            "correct_answer": "True" if is_true else "False",
            "explanation": explanation
        })
        if len(quiz) >= num_questions:
            break

    return quiz
