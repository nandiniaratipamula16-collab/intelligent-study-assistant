"""
Interactive Flashcard Generator with Spaced Repetition System (SRS),
deck import/export, and card rating tracking.
"""

import json
import csv
import io
import re
from typing import List, Dict, Any, Optional
from .ai_engine import AIEngine


class FlashcardDeck:
    def __init__(self, cards: Optional[List[Dict[str, Any]]] = None):
        # Card schema: {"id": int, "question": str, "answer": str, "category": str, "box": int, "reviews": int}
        self.cards: List[Dict[str, Any]] = cards or []

    def add_card(self, question: str, answer: str, category: str = "General") -> Dict[str, Any]:
        card_id = len(self.cards) + 1
        new_card = {
            "id": card_id,
            "question": question.strip(),
            "answer": answer.strip(),
            "category": category.strip() or "General",
            "box": 1,  # 1 = Learning, 2 = Review, 3 = Mastered
            "reviews": 0
        }
        self.cards.append(new_card)
        return new_card

    def update_rating(self, card_index: int, rating: str):
        """Update spaced repetition box based on rating: 'hard', 'good', 'easy'."""
        if 0 <= card_index < len(self.cards):
            card = self.cards[card_index]
            card["reviews"] = card.get("reviews", 0) + 1
            current_box = card.get("box", 1)

            if rating == "easy":
                card["box"] = min(3, current_box + 1)
            elif rating == "hard":
                card["box"] = 1
            elif rating == "good":
                card["box"] = max(1, current_box)

    def get_stats(self) -> Dict[str, Any]:
        total = len(self.cards)
        if total == 0:
            return {"total": 0, "learning": 0, "review": 0, "mastered": 0, "mastery_rate": 0.0}
        
        learning = sum(1 for c in self.cards if c.get("box", 1) == 1)
        review = sum(1 for c in self.cards if c.get("box", 1) == 2)
        mastered = sum(1 for c in self.cards if c.get("box", 1) == 3)
        mastery_rate = round((mastered / total) * 100, 1)

        return {
            "total": total,
            "learning": learning,
            "review": review,
            "mastered": mastered,
            "mastery_rate": mastery_rate
        }

    def export_to_json(self) -> str:
        return json.dumps(self.cards, indent=2)

    def export_to_csv(self) -> str:
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Question", "Answer", "Category", "Box", "Reviews"])
        for c in self.cards:
            writer.writerow([c["question"], c["answer"], c.get("category", "General"), c.get("box", 1), c.get("reviews", 0)])
        return output.getvalue()

    @classmethod
    def from_json(cls, json_str: str) -> "FlashcardDeck":
        try:
            cards = json.loads(json_str)
            return cls(cards=cards)
        except Exception:
            return cls()

    @classmethod
    def from_csv(cls, csv_str: str) -> "FlashcardDeck":
        cards = []
        try:
            reader = csv.reader(io.StringIO(csv_str))
            header = next(reader, None)
            for idx, row in enumerate(reader):
                if len(row) >= 2:
                    cards.append({
                        "id": idx + 1,
                        "question": row[0].strip(),
                        "answer": row[1].strip(),
                        "category": row[2].strip() if len(row) > 2 else "General",
                        "box": int(row[3]) if len(row) > 3 and row[3].isdigit() else 1,
                        "reviews": int(row[4]) if len(row) > 4 and row[4].isdigit() else 0
                    })
        except Exception:
            pass
        return cls(cards=cards)


def generate_flashcards(text: str, ai_engine: AIEngine, num_cards: int = 8) -> List[Dict[str, Any]]:
    """Generate high-yield Q&A flashcards using Gemini or offline heuristic engine."""
    if not text.strip():
        return []

    if ai_engine.is_ai_online:
        return _generate_ai_flashcards(text, ai_engine, num_cards)
    else:
        return _generate_heuristic_flashcards(text, ai_engine, num_cards)


def _generate_ai_flashcards(text: str, ai_engine: AIEngine, num_cards: int) -> List[Dict[str, Any]]:
    """Prompt Gemini to create high-retention active-recall flashcards."""
    prompt = f"""You are a master educator creating high-yield active recall flashcards.
Extract the most critical concepts, mechanisms, causes/effects, and definitions from the study material below.

Study Material:
\"\"\"{text[:9000]}\"\"\"

Create exactly {num_cards} flashcards.
Return a valid JSON array of objects, each with:
- "question": Direct, thought-provoking question testing deep comprehension (avoid vague or trivial queries).
- "answer": Clear, concise, accurate answer (2-4 sentences max).
- "category": Short domain subcategory tag (e.g., "Definition", "Mechanism", "Application", "Comparison").

Respond ONLY with valid JSON array format, like:
[
  {{"question": "What is...", "answer": "It is...", "category": "Concept"}}
]
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
        
        cards_raw = json.loads(clean)
        deck = []
        for idx, item in enumerate(cards_raw[:num_cards]):
            deck.append({
                "id": idx + 1,
                "question": item.get("question", "").strip(),
                "answer": item.get("answer", "").strip(),
                "category": item.get("category", "General"),
                "box": 1,
                "reviews": 0
            })
        return deck
    except Exception as e:
        return _generate_heuristic_flashcards(text, ai_engine, num_cards)


def _generate_heuristic_flashcards(text: str, ai_engine: AIEngine, num_cards: int) -> List[Dict[str, Any]]:
    """Extract flashcards from definition patterns, headings, and bullet points without an API key."""
    cards = []
    
    # 1. Look for definition patterns
    definitions = ai_engine.extract_key_definitions(text)
    for d in definitions:
        cards.append({
            "id": len(cards) + 1,
            "question": f"What is {d['term']} and why is it significant?",
            "answer": d["definition"],
            "category": "Key Concept",
            "box": 1,
            "reviews": 0
        })
        if len(cards) >= num_cards:
            return cards

    # 2. Look for bullet points with colon syntax (e.g. "- Term: explanation")
    bullet_patterns = re.findall(r'^[*\-]\s+([^:\n]{3,40}):\s+(.+)$', text, re.MULTILINE)
    for term, desc in bullet_patterns:
        cards.append({
            "id": len(cards) + 1,
            "question": f"Explain the role or function of: {term.strip()}",
            "answer": desc.strip(),
            "category": "Details & Mechanisms",
            "box": 1,
            "reviews": 0
        })
        if len(cards) >= num_cards:
            return cards

    # 3. Look for section headings
    headings = re.findall(r'^(?:##|###)\s+(.+)$', text, re.MULTILINE)
    for h in headings:
        clean_h = h.strip()
        cards.append({
            "id": len(cards) + 1,
            "question": f"Summarize the main principles under '{clean_h}'.",
            "answer": f"Refer to the section '{clean_h}' in your study material for the comprehensive breakdown.",
            "category": "Topic Overview",
            "box": 1,
            "reviews": 0
        })
        if len(cards) >= num_cards:
            return cards

    # 4. Fallback if short or plain text
    keywords = [kw for kw, _ in ai_engine.extract_keywords(text, top_n=num_cards)]
    for kw in keywords:
        cards.append({
            "id": len(cards) + 1,
            "question": f"What does '{kw.capitalize()}' refer to in this context?",
            "answer": f"'{kw.capitalize()}' is a central keyword frequently emphasized in the notes.",
            "category": "Keyword",
            "box": 1,
            "reviews": 0
        })
        if len(cards) >= num_cards:
            break

    return cards
