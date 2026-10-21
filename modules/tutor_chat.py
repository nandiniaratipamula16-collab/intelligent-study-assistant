"""
AI Tutor chat module with conversational memory, document context grounding,
and pedagogical modes (Feynman Technique, Socratic Tutor, Exam Coach).
"""

import re
from typing import List, Dict, Any, Optional
from .ai_engine import AIEngine


class TutorChat:
    MODES = {
        "Academic Tutor": "You are an encouraging and erudite academic tutor. Provide rigorous, clear, and structured explanations.",
        "Feynman Technique": "You are Richard Feynman. Explain complex concepts in remarkably simple terms, using intuitive real-world analogies that a 10-year-old could easily grasp. Avoid opaque jargon.",
        "Socratic Mentor": "You are a Socratic tutor. Guide the student by asking thoughtful, probing questions that help them discover the answer themselves. Do not simply blurt out solutions.",
        "Exam Prep Coach": "You are an intensive exam prep coach. Focus on high-yield test points, common trap questions, memory mnemonics, and how to formulate full-mark answers."
    }

    def __init__(self, ai_engine: AIEngine):
        self.ai_engine = ai_engine

    def ask(self, user_query: str, study_context: str, chat_history: List[Dict[str, str]], mode: str = "Academic Tutor") -> str:
        """Process user query grounded on study material context."""
        if not user_query.strip():
            return "Please type a question or select a quick study prompt."

        system_instruction = self.MODES.get(mode, self.MODES["Academic Tutor"])

        if self.ai_engine.is_ai_online:
            return self._ask_ai(user_query, study_context, chat_history, system_instruction)
        else:
            return self._ask_heuristic(user_query, study_context, mode)

    def _ask_ai(self, user_query: str, study_context: str, chat_history: List[Dict[str, str]], system_instruction: str) -> str:
        """Generate response via Gemini with conversational context."""
        # Format recent history (last 4 turns)
        history_formatted = ""
        recent_history = chat_history[-6:] if len(chat_history) > 6 else chat_history
        for turn in recent_history:
            role = "Student" if turn["role"] == "user" else "Tutor"
            history_formatted += f"{role}: {turn['content']}\n"

        prompt = f"""You are an intelligent study assistant. Your job is to answer the student's question accurately, grounded in their provided study material whenever relevant.

STUDY CONTEXT:
\"\"\"{study_context[:8000]}\"\"\"

PREVIOUS CONVERSATION:
{history_formatted}

STUDENT QUESTION:
{user_query}

Provide a well-structured, insightful, markdown-formatted response with bold terms, bullet points, or analogies where helpful.
"""
        return self.ai_engine.generate_text(prompt, system_instruction=system_instruction)

    def _ask_heuristic(self, user_query: str, study_context: str, mode: str) -> str:
        """Offline heuristic answering using text search and keyword extraction."""
        query_words = set(re.findall(r'\b[a-zA-Z]{3,}\b', user_query.lower()))
        sentences = [s.strip() for s in re.split(r'[.!?\n]+', study_context) if len(s.strip()) > 20]
        
        # Rank sentences by query word match
        matched = []
        for s in sentences:
            s_words = set(re.findall(r'\b[a-zA-Z]{3,}\b', s.lower()))
            common = query_words.intersection(s_words)
            if common:
                matched.append((len(common), s))
                
        matched.sort(key=lambda x: x[0], reverse=True)
        top_matches = [m[1] for m in matched[:3]]

        prefix = f"🎓 **Tutor Response ({mode} - Local Engine)**\n\n"
        if top_matches:
            body = (
                "Here are the most pertinent passages from your notes addressing your inquiry:\n\n" +
                "\n\n".join(f"> \"{match}\"" for match in top_matches) +
                "\n\n*Tip: Connect your Gemini API Key in the left sidebar to unlock conversational dialogue and personalized analogies!*"
            )
        else:
            body = (
                f"I looked through your study material for concepts related to **\"{user_query}\"**.\n\n"
                "To get deep, conversational explanations or when asking questions outside the immediate text, "
                "please enter a Google Gemini API Key in the sidebar settings."
            )
        return prefix + body
