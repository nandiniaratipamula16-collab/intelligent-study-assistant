"""
Summarization module providing executive summaries, bullet takeaways,
TL;DRs, key definitions, and concept mindmaps.
"""

import re
from typing import Dict, Any, List
from .ai_engine import AIEngine


def generate_summary(text: str, ai_engine: AIEngine, summary_type: str = "comprehensive") -> Dict[str, Any]:
    """Generate multi-format summaries: Executive, Bullet Points, TL;DR, and Mermaid Mindmap."""
    if not text.strip():
        return {
            "tldr": "No text provided.",
            "executive": "Please provide or upload study material.",
            "bullet_points": [],
            "definitions": [],
            "mermaid_mindmap": ""
        }

    if ai_engine.is_ai_online:
        return _generate_ai_summary(text, ai_engine, summary_type)
    else:
        return _generate_heuristic_summary(text, ai_engine)


def _generate_ai_summary(text: str, ai_engine: AIEngine, summary_type: str) -> Dict[str, Any]:
    """Generate high-fidelity structured summary using Gemini."""
    prompt = f"""You are an elite academic tutor and study assistant. Analyze the following study material thoroughly.

Study Material:
\"\"\"{text[:10000]}\"\"\"

Generate a JSON response with the exact following keys:
1. "tldr": A punchy 1-2 sentence core takeaway.
2. "executive": A cohesive 2-3 paragraph executive summary covering major principles and nuances.
3. "bullet_points": An array of 5-8 comprehensive bullet point takeaways.
4. "definitions": An array of objects with "term" and "definition" for the 4-8 most crucial concepts.
5. "mermaid_mindmap": A clean, valid Mermaid.js flowchart code block (syntax: flowchart TD or graph TD) illustrating the hierarchy of main topic -> subtopics -> key mechanisms. Do NOT enclose in markdown code fence in the JSON value, just raw mermaid code string starting with 'graph TD'.

Respond ONLY with valid JSON.
"""
    try:
        raw_output = ai_engine.generate_text(prompt)
        # Clean json output from markdown fences if any
        clean_json = raw_output.strip()
        if clean_json.startswith("```json"):
            clean_json = clean_json[7:]
        if clean_json.startswith("```"):
            clean_json = clean_json[3:]
        if clean_json.endswith("```"):
            clean_json = clean_json[:-3]
        clean_json = clean_json.strip()
        
        parsed = json.loads(clean_json)
        # Ensure fallback for mindmap
        if "mermaid_mindmap" not in parsed or not parsed["mermaid_mindmap"]:
            parsed["mermaid_mindmap"] = _build_heuristic_mermaid(text)
        return parsed
    except Exception as e:
        # Fall back gracefully to heuristic generator if parsing fails
        fallback = _generate_heuristic_summary(text, ai_engine)
        fallback["executive"] = f"(Note: AI response fallback triggered. Showing structured heuristic summary)\n\n" + fallback["executive"]
        return fallback


def _generate_heuristic_summary(text: str, ai_engine: AIEngine) -> Dict[str, Any]:
    """Generate high-quality rule-based/statistical summary without requiring an active API key."""
    # Split sentences
    sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if len(s.strip()) > 25]
    
    # Extract keywords
    keywords = [kw for kw, _ in ai_engine.extract_keywords(text, top_n=20)]
    
    # Score sentences based on keyword overlap and position
    scored_sentences = []
    for idx, sentence in enumerate(sentences):
        lower_sent = sentence.lower()
        score = sum(1.5 for kw in keywords if kw in lower_sent)
        # Boost earlier sentences in paragraphs or overall text
        if idx < 3:
            score += 2.0
        # Boost sentences with definitions or importance cues
        if any(w in lower_sent for w in ["important", "crucial", "fundamental", "defined as", "consists of", "primary"]):
            score += 2.5
        scored_sentences.append((score, sentence))

    scored_sentences.sort(key=lambda x: x[0], reverse=True)
    top_sentences = [s for _, s in scored_sentences[:6]]
    
    # TL;DR (top 1-2 most informative sentences)
    tldr = " ".join(top_sentences[:2]) if top_sentences else "No significant text detected."
    
    # Executive summary
    exec_sentences = [s for _, s in scored_sentences[:5]]
    executive = " ".join(exec_sentences) if exec_sentences else text[:500]
    
    # Bullet points
    bullet_points = top_sentences[1:7] if len(top_sentences) > 1 else top_sentences
    
    # Definitions
    definitions = ai_engine.extract_key_definitions(text)
    if not definitions and keywords:
        definitions = [{"term": kw.capitalize(), "definition": f"Core concept identified frequently across the study material."} for kw in keywords[:5]]

    # Mindmap
    mermaid_mindmap = _build_heuristic_mermaid(text)

    return {
        "tldr": tldr,
        "executive": executive,
        "bullet_points": bullet_points,
        "definitions": definitions,
        "mermaid_mindmap": mermaid_mindmap
    }


def _build_heuristic_mermaid(text: str) -> str:
    """Construct a clean Mermaid.js graph based on markdown headers and key themes."""
    lines = text.split("\n")
    main_title = "Study Topic"
    subtopics = []
    
    for line in lines:
        line_clean = line.strip()
        if line_clean.startswith("# ") and main_title == "Study Topic":
            main_title = line_clean.replace("#", "").strip()
        elif line_clean.startswith("## ") and len(subtopics) < 5:
            sub = line_clean.replace("##", "").strip()
            # Clean special characters for mermaid safety
            sub = re.sub(r'[^a-zA-Z0-9\s]', '', sub)
            if sub:
                subtopics.append(sub)
                
    # Safe id generator
    safe_main = re.sub(r'[^a-zA-Z0-9]', '', main_title) or "Topic"
    mermaid_code = ["graph TD", f'    {safe_main}["📘 {main_title}"]']
    
    if not subtopics:
        subtopics = ["Key Concepts", "Core Mechanisms", "Practical Applications", "Critical Insights"]
        
    for idx, sub in enumerate(subtopics):
        node_id = f"Sub_{idx}"
        mermaid_code.append(f'    {safe_main} --> {node_id}["{sub}"]')
        # Add sample subnodes
        leaf_1 = f"Leaf_{idx}_1"
        leaf_2 = f"Leaf_{idx}_2"
        mermaid_code.append(f'    {node_id} --> {leaf_1}["Foundations"]')
        mermaid_code.append(f'    {node_id} --> {leaf_2}["Analysis & Review"]')
        
    return "\n".join(mermaid_code)
