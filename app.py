"""
Intelligent Study Assistant - Main Streamlit Application
A comprehensive AI-powered web platform for students and lifelong learners.
"""

import os
import datetime
import streamlit as st

from modules.document_processor import extract_text_from_uploaded_file, compute_text_metrics, clean_and_normalize_text
from modules.ai_engine import AIEngine
from modules.summarizer import generate_summary
from modules.flashcards import FlashcardDeck, generate_flashcards
from modules.quiz_generator import generate_quiz
from modules.tutor_chat import TutorChat
from modules.study_planner import generate_study_plan
from modules.analytics import StudyAnalytics
from assets.sample_notes import SAMPLE_NOTES


# -------------------------------------------------------------
# 1. PAGE CONFIGURATION & STYLING
# -------------------------------------------------------------
st.set_page_config(
    page_title="Intelligent Study Assistant",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load custom CSS
css_path = os.path.join(os.path.dirname(__file__), "assets", "styles.css")
if os.path.exists(css_path):
    with open(css_path, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


# -------------------------------------------------------------
# 2. SESSION STATE INITIALIZATION
# -------------------------------------------------------------
if "ai_engine" not in st.session_state:
    st.session_state.ai_engine = AIEngine()

if "study_text" not in st.session_state:
    # Default to first sample note for instant zero-click testing
    default_title = "Artificial Intelligence & Machine Learning"
    st.session_state.active_doc_title = default_title
    st.session_state.study_text = SAMPLE_NOTES[default_title]
    st.session_state.doc_metrics = compute_text_metrics(st.session_state.study_text)

if "summary_data" not in st.session_state:
    st.session_state.summary_data = None

if "flashcards" not in st.session_state:
    st.session_state.flashcards = []
if "card_index" not in st.session_state:
    st.session_state.card_index = 0
if "card_flipped" not in st.session_state:
    st.session_state.card_flipped = False

if "quiz_data" not in st.session_state:
    st.session_state.quiz_data = []
if "quiz_submitted" not in st.session_state:
    st.session_state.quiz_submitted = False
if "user_quiz_answers" not in st.session_state:
    st.session_state.user_quiz_answers = {}
if "quiz_history" not in st.session_state:
    st.session_state.quiz_history = []

if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {"role": "assistant", "content": "👋 Hello! I am your Intelligent Study Assistant. Ask me anything about your study notes, request analogies, or test your comprehension!"}
    ]

if "pomodoro_count" not in st.session_state:
    st.session_state.pomodoro_count = 0
if "study_plan" not in st.session_state:
    st.session_state.study_plan = None


# -------------------------------------------------------------
# 3. SIDEBAR: SETTINGS & DOCUMENT INGESTION
# -------------------------------------------------------------
with st.sidebar:
    st.markdown("## ⚙️ Control Center")
    
    # AI Engine Settings Expander
    with st.expander("🤖 AI Engine & Model Settings", expanded=True):
        api_key_input = st.text_input(
            "Google Gemini API Key",
            type="password",
            value=st.session_state.ai_engine.api_key,
            help="Free API key from Google AI Studio (aistudio.google.com). Leave blank to use the built-in Intelligent Offline Heuristic Engine!"
        )
        selected_model = st.selectbox(
            "Gemini Model",
            options=["gemini-2.5-flash", "gemini-1.5-flash", "gemini-1.5-pro"],
            index=0
        )
        if api_key_input != st.session_state.ai_engine.api_key or selected_model != st.session_state.ai_engine.model_name:
            st.session_state.ai_engine.update_credentials(api_key_input, selected_model)
        
        # Engine status badge
        if st.session_state.ai_engine.is_ai_online:
            st.success("🟢 Online Mode: Gemini Active")
        else:
            st.info("🟡 Smart Heuristic Mode: Active (No API Key Required)")

    st.markdown("---")
    st.markdown("### 📚 Study Materials")

    # Sample Notes Quick-Loader
    sample_choice = st.selectbox(
        "Load Pre-packaged Topic:",
        options=["(Select a Sample Topic)"] + list(SAMPLE_NOTES.keys()),
        index=1 if st.session_state.active_doc_title in SAMPLE_NOTES else 0
    )
    if sample_choice != "(Select a Sample Topic)" and sample_choice != st.session_state.active_doc_title:
        st.session_state.active_doc_title = sample_choice
        st.session_state.study_text = SAMPLE_NOTES[sample_choice]
        st.session_state.doc_metrics = compute_text_metrics(st.session_state.study_text)
        # Reset dependent states for new document
        st.session_state.summary_data = None
        st.session_state.flashcards = []
        st.session_state.quiz_data = []
        st.session_state.quiz_submitted = False
        st.rerun()

    # Upload Document
    uploaded_doc = st.file_uploader("Upload Notes / Textbook (PDF, DOCX, TXT):", type=["pdf", "docx", "txt", "md"])
    if uploaded_doc is not None:
        if st.button("📥 Parse & Ingest Uploaded File", use_container_width=True):
            with st.spinner("Extracting and analyzing document content..."):
                extracted = extract_text_from_uploaded_file(uploaded_doc)
                if extracted and not extracted.startswith("Error"):
                    st.session_state.study_text = clean_and_normalize_text(extracted)
                    st.session_state.active_doc_title = uploaded_doc.name
                    st.session_state.doc_metrics = compute_text_metrics(st.session_state.study_text)
                    st.session_state.summary_data = None
                    st.session_state.flashcards = []
                    st.session_state.quiz_data = []
                    st.session_state.quiz_submitted = False
                    st.success(f"Parsed {uploaded_doc.name} successfully!")
                    st.rerun()
                else:
                    st.error(extracted or "Could not extract text from document.")

    # Direct Text Input / Scratchpad
    with st.expander("✍️ Paste / Edit Raw Notes"):
        user_notes_input = st.text_area(
            "Edit active study text:",
            value=st.session_state.study_text[:5000],
            height=150,
            help="Edits apply when you click Update Notes below."
        )
        if st.button("Update Active Notes", use_container_width=True):
            st.session_state.study_text = user_notes_input
            st.session_state.active_doc_title = "Custom Notes"
            st.session_state.doc_metrics = compute_text_metrics(user_notes_input)
            st.session_state.summary_data = None
            st.rerun()

    # Text Metrics Sidebar Display
    st.markdown("---")
    st.markdown("### 📊 Document Overview")
    metrics = st.session_state.doc_metrics or compute_text_metrics(st.session_state.study_text)
    m1, m2 = st.columns(2)
    with m1:
        st.metric("Total Words", f"{metrics['word_count']:,}")
        st.metric("Est. Read Time", f"{metrics['reading_time_min']}m")
    with m2:
        st.metric("Sentences", f"{metrics['sentence_count']}")
        st.metric("Readability", f"{metrics['flesch_reading_ease']}/100")
    st.caption(f"**Level:** {metrics['difficulty_label']}")


# -------------------------------------------------------------
# 4. APP HEADER HERO
# -------------------------------------------------------------
st.markdown(f"""
<div class="main-header">
    <h1>🎓 Intelligent Study Assistant</h1>
    <p>Active Learning Platform • Smart Summaries • Flashcards (Leitner SRS) • Exam Simulator • AI Feynman Tutor</p>
</div>
""", unsafe_allow_html=True)

# Active topic banner
st.info(f"📖 **Active Document:** `{st.session_state.active_doc_title}` | **Word Count:** {metrics['word_count']:,} words")


# -------------------------------------------------------------
# 5. MAIN NAVIGATION TABS
# -------------------------------------------------------------
tab_summary, tab_flashcards, tab_quiz, tab_tutor, tab_planner, tab_analytics = st.tabs([
    "📑 Summary & Mind Map",
    "🗂️ Interactive Flashcards",
    "📝 AI Practice Quiz",
    "💬 'Ask My Notes' Tutor",
    "⏱️ Study Planner & Pomodoro",
    "📊 Progress Analytics"
])


# =============================================================
# TAB 1: SUMMARY & MIND MAP
# =============================================================
with tab_summary:
    st.markdown("### 📑 Intelligent Summarization & Concept Mind Map")
    
    col_btn1, col_btn2 = st.columns([1, 4])
    with col_btn1:
        if st.button("🚀 Generate Summary", type="primary", use_container_width=True):
            with st.spinner("Synthesizing core concepts, executive summary, and mind map..."):
                st.session_state.summary_data = generate_summary(
                    st.session_state.study_text,
                    st.session_state.ai_engine
                )
                st.rerun()

    if st.session_state.summary_data is None:
        st.write("Click **'Generate Summary'** above to generate an executive overview, bullet takeaways, and visual concept map for this material.")
    else:
        data = st.session_state.summary_data

        # TL;DR Callout
        st.markdown(f"""
        <div style="background-color: #f0fdf4; border-left: 5px solid #22c55e; padding: 1rem; border-radius: 8px; margin: 1rem 0;">
            <strong style="color: #15803d; font-size: 1.1rem;">⚡ Quick TL;DR:</strong><br>
            <span style="font-size: 1.05rem; color: #166534;">{data.get('tldr', 'No TLDR generated.')}</span>
        </div>
        """, unsafe_allow_html=True)

        col_s1, col_s2 = st.columns([3, 2])
        
        with col_s1:
            st.markdown("#### 📖 Executive Summary")
            st.markdown(data.get("executive", "N/A"))

            st.markdown("#### 🔑 Core Takeaways & High-Yield Insights")
            bullets = data.get("bullet_points", [])
            for bp in bullets:
                st.markdown(f"- {bp}")

        with col_s2:
            st.markdown("#### 📘 Key Terminology & Definitions")
            defs = data.get("definitions", [])
            if defs:
                for item in defs:
                    with st.container():
                        st.markdown(f"""
                        <div style="background: rgba(243, 244, 246, 0.7); border: 1px solid #e5e7eb; border-radius: 8px; padding: 0.75rem; margin-bottom: 0.5rem;">
                            <strong style="color: #4f46e5;">{item.get('term', '')}</strong>: 
                            <span style="font-size: 0.95rem;">{item.get('definition', '')}</span>
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.caption("No explicit definitions extracted.")

        st.markdown("---")
        st.markdown("#### 🧠 Conceptual Mind Map")
        st.caption("Visual hierarchy illustrating relationships between main principles and sub-components.")
        mermaid_code = data.get("mermaid_mindmap", "")
        if mermaid_code:
            try:
                # Render mermaid using markdown code fence
                st.markdown(f"```mermaid\n{mermaid_code}\n```")
            except Exception:
                st.code(mermaid_code, language="mermaid")
        else:
            st.caption("Mind map not available.")


# =============================================================
# TAB 2: INTERACTIVE FLASHCARDS & LEITNER SRS
# =============================================================
with tab_flashcards:
    st.markdown("### 🗂️ Interactive Flashcard Deck (Spaced Repetition)")
    
    top_col1, top_col2, top_col3 = st.columns([2, 1, 1])
    with top_col1:
        num_cards_to_gen = st.slider("Number of cards to generate:", 4, 15, 8)
    with top_col2:
        if st.button("✨ Auto-Generate Deck", type="primary", use_container_width=True):
            with st.spinner("Extracting high-retention flashcards..."):
                new_deck = generate_flashcards(st.session_state.study_text, st.session_state.ai_engine, num_cards_to_gen)
                st.session_state.flashcards = new_deck
                st.session_state.card_index = 0
                st.session_state.card_flipped = False
                st.rerun()
    with top_col3:
        if st.button("🔀 Shuffle Cards", use_container_width=True):
            import random
            if st.session_state.flashcards:
                random.shuffle(st.session_state.flashcards)
                st.session_state.card_index = 0
                st.session_state.card_flipped = False
                st.rerun()

    deck_handler = FlashcardDeck(st.session_state.flashcards)
    stats = deck_handler.get_stats()

    # Progress stats bar
    stat_c1, stat_c2, stat_c3, stat_c4 = st.columns(4)
    with stat_c1:
        st.metric("Total Cards", stats["total"])
    with stat_c2:
        st.metric("Box 1 (Learning)", stats["learning"])
    with stat_c3:
        st.metric("Box 2 (Review)", stats["review"])
    with stat_c4:
        st.metric("Box 3 (Mastered)", f"{stats['mastered']} ({stats['mastery_rate']}%)")

    st.markdown("---")

    if not st.session_state.flashcards:
        st.info("No cards in the deck yet! Click **'Auto-Generate Deck'** above or add custom cards in the expander below.")
    else:
        # Clamp card index
        idx = max(0, min(st.session_state.card_index, len(st.session_state.flashcards) - 1))
        st.session_state.card_index = idx
        current_card = st.session_state.flashcards[idx]

        # Box badge
        box_num = current_card.get("box", 1)
        box_labels = {1: ("Box 1 • Learning", "badge-yellow"), 2: ("Box 2 • Reviewing", "badge-indigo"), 3: ("Box 3 • Mastered", "badge-green")}
        box_text, box_class = box_labels.get(box_num, ("Box 1", "badge-yellow"))

        # Flashcard Container
        st.markdown(f"""
        <div class="flashcard-box">
            <span class="flashcard-category">{current_card.get('category', 'General')}</span>
            <span class="flashcard-status badge-pill {box_class}">{box_text}</span>
            <div class="flashcard-text">
                {"<b>Answer:</b><br>" + current_card.get('answer', '') if st.session_state.card_flipped else "<b>Question:</b><br>" + current_card.get('question', '')}
            </div>
            <div class="flashcard-tip">
                {'(Click "Flip Card" below to view question)' if st.session_state.card_flipped else '(Click "Flip Card" below to reveal answer)'}
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Card Interaction Controls
        c_prev, c_flip, c_next = st.columns([1, 2, 1])
        with c_prev:
            if st.button("⬅️ Previous Card", use_container_width=True, disabled=(idx == 0)):
                st.session_state.card_index -= 1
                st.session_state.card_flipped = False
                st.rerun()
        with c_flip:
            btn_label = "🔄 Flip to Question" if st.session_state.card_flipped else "🔄 Flip to Reveal Answer"
            if st.button(btn_label, type="secondary", use_container_width=True):
                st.session_state.card_flipped = not st.session_state.card_flipped
                st.rerun()
        with c_next:
            if st.button("Next Card ➡️", use_container_width=True, disabled=(idx >= len(st.session_state.flashcards) - 1)):
                st.session_state.card_index += 1
                st.session_state.card_flipped = False
                st.rerun()

        # Spaced Repetition Rating Buttons
        st.markdown("##### Rate Your Recall for this Card:")
        r_c1, r_c2, r_c3 = st.columns(3)
        with r_c1:
            if st.button("❌ Hard (Reset to Box 1)", use_container_width=True):
                deck_handler.update_rating(idx, "hard")
                st.session_state.flashcards = deck_handler.cards
                if idx < len(st.session_state.flashcards) - 1:
                    st.session_state.card_index += 1
                st.session_state.card_flipped = False
                st.rerun()
        with r_c2:
            if st.button("⚠️ Good (Keep in Box)", use_container_width=True):
                deck_handler.update_rating(idx, "good")
                st.session_state.flashcards = deck_handler.cards
                if idx < len(st.session_state.flashcards) - 1:
                    st.session_state.card_index += 1
                st.session_state.card_flipped = False
                st.rerun()
        with r_c3:
            if st.button("✅ Easy (Advance to Next Box)", use_container_width=True):
                deck_handler.update_rating(idx, "easy")
                st.session_state.flashcards = deck_handler.cards
                if idx < len(st.session_state.flashcards) - 1:
                    st.session_state.card_index += 1
                st.session_state.card_flipped = False
                st.rerun()

        st.caption(f"Card {idx + 1} of {len(st.session_state.flashcards)} • Total reviews logged for this card: {current_card.get('reviews', 0)}")

    # Deck Import / Export & Add Custom Card
    with st.expander("🛠️ Deck Management (Add Custom Cards, Import & Export)"):
        m_c1, m_c2 = st.columns(2)
        with m_c1:
            st.markdown("###### Add Custom Card")
            custom_q = st.text_input("Question:")
            custom_a = st.text_area("Answer:", height=80)
            custom_cat = st.text_input("Category / Tag:", value="General")
            if st.button("➕ Add Card to Deck"):
                if custom_q.strip() and custom_a.strip():
                    deck_handler.add_card(custom_q, custom_a, custom_cat)
                    st.session_state.flashcards = deck_handler.cards
                    st.success("Card added!")
                    st.rerun()
                else:
                    st.warning("Please enter both question and answer.")

        with m_c2:
            st.markdown("###### Export & Import")
            if st.session_state.flashcards:
                st.download_button(
                    "💾 Export Deck as JSON",
                    data=deck_handler.export_to_json(),
                    file_name="study_deck.json",
                    mime="application/json",
                    use_container_width=True
                )
                st.download_button(
                    "📄 Export Deck as CSV (Anki Compatible)",
                    data=deck_handler.export_to_csv(),
                    file_name="study_deck.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            
            uploaded_deck = st.file_uploader("Import JSON/CSV Deck:", type=["json", "csv"])
            if uploaded_deck is not None:
                if st.button("Import Deck File", use_container_width=True):
                    content = uploaded_deck.getvalue().decode("utf-8", errors="ignore")
                    if uploaded_deck.name.endswith(".json"):
                        imported = FlashcardDeck.from_json(content)
                    else:
                        imported = FlashcardDeck.from_csv(content)
                    if imported.cards:
                        st.session_state.flashcards = imported.cards
                        st.session_state.card_index = 0
                        st.success(f"Imported {len(imported.cards)} flashcards!")
                        st.rerun()


# =============================================================
# TAB 3: AI PRACTICE QUIZ & EXAM SIMULATOR
# =============================================================
with tab_quiz:
    st.markdown("### 📝 AI Practice Quiz & Exam Simulator")
    st.caption("Test your mastery with active recall questions, instant scoring, and in-depth conceptual explanations.")

    q_col1, q_col2, q_col3 = st.columns([1, 1, 1])
    with q_col1:
        num_q = st.select_slider("Number of Questions:", options=[3, 5, 8, 10], value=5)
    with q_col2:
        diff_level = st.selectbox("Exam Difficulty:", ["Standard / High School", "College / Intermediate", "Advanced / Graduate"], index=1)
    with q_col3:
        st.write("")
        st.write("")
        if st.button("🎯 Generate New Quiz", type="primary", use_container_width=True):
            with st.spinner("Crafting exam questions and distractor choices..."):
                st.session_state.quiz_data = generate_quiz(st.session_state.study_text, st.session_state.ai_engine, num_q, diff_level)
                st.session_state.quiz_submitted = False
                st.session_state.user_quiz_answers = {}
                st.rerun()

    if not st.session_state.quiz_data:
        st.info("Click **'Generate New Quiz'** to create an interactive practice test from your study material.")
    else:
        st.markdown("---")
        
        # Display Quiz Form
        with st.form("quiz_form"):
            for q_idx, q in enumerate(st.session_state.quiz_data):
                st.markdown(f"**Question {q_idx + 1}:** {q['question']}")
                q_id = str(q.get("id", q_idx))
                
                options = q.get("options", ["True", "False"])
                st.radio(
                    label=f"Select your answer for Q{q_idx + 1}:",
                    options=options,
                    key=f"quiz_opt_{q_id}",
                    index=None,
                    label_visibility="collapsed"
                )
                st.markdown("<br>", unsafe_allow_html=True)
            
            submit_quiz = st.form_submit_button("🏁 Submit Quiz for Grading", type="primary", use_container_width=True)

        if submit_quiz:
            st.session_state.quiz_submitted = True
            # Collect answers
            total_correct = 0
            for q_idx, q in enumerate(st.session_state.quiz_data):
                q_id = str(q.get("id", q_idx))
                ans = st.session_state.get(f"quiz_opt_{q_id}")
                st.session_state.user_quiz_answers[q_id] = ans
                if ans and ans == q.get("correct_answer"):
                    total_correct += 1
            
            score_pct = round((total_correct / len(st.session_state.quiz_data)) * 100, 1)
            # Record in quiz history
            st.session_state.quiz_history.append({
                "attempt": len(st.session_state.quiz_history) + 1,
                "score_percent": score_pct,
                "score": f"{total_correct}/{len(st.session_state.quiz_data)}",
                "timestamp": datetime.datetime.now().strftime("%H:%M:%S")
            })
            st.rerun()

        # Display Results and Explanations if submitted
        if st.session_state.quiz_submitted:
            st.markdown("---")
            total_q = len(st.session_state.quiz_data)
            correct_count = sum(1 for q_idx, q in enumerate(st.session_state.quiz_data) if st.session_state.user_quiz_answers.get(str(q.get("id", q_idx))) == q.get("correct_answer"))
            score_pct = round((correct_count / total_q) * 100, 1)
            
            if score_pct >= 90:
                grade_color = "#10b981"
                grade_title = "🏆 Outstanding Mastery! (Grade: A+)"
            elif score_pct >= 75:
                grade_color = "#3b82f6"
                grade_title = "👍 Solid Comprehension! (Grade: B)"
            elif score_pct >= 60:
                grade_color = "#f59e0b"
                grade_title = "📚 Passing, Needs Revision! (Grade: C)"
            else:
                grade_color = "#ef4444"
                grade_title = "⚠️ Review Study Material (Grade: Needs Work)"

            st.markdown(f"""
            <div style="background-color: rgba(255, 255, 255, 0.9); border: 2px solid {grade_color}; border-radius: 12px; padding: 1.5rem; text-align: center; margin-bottom: 1.5rem;">
                <h3 style="color: {grade_color}; margin: 0;">{grade_title}</h3>
                <h1 style="color: {grade_color}; margin: 0.5rem 0; font-size: 2.5rem;">{score_pct}%</h1>
                <p style="color: #6b7280; margin: 0;">You answered <b>{correct_count}</b> out of <b>{total_q}</b> questions correctly.</p>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("#### 🔍 Detailed Answer Explanations:")
            for q_idx, q in enumerate(st.session_state.quiz_data):
                q_id = str(q.get("id", q_idx))
                user_ans = st.session_state.user_quiz_answers.get(q_id)
                correct_ans = q.get("correct_answer")
                is_correct = (user_ans == correct_ans)

                icon = "✅" if is_correct else "❌"
                card_bg = "#f0fdf4" if is_correct else "#fef2f2"
                card_border = "#86efac" if is_correct else "#fca5a5"

                st.markdown(f"""
                <div style="background-color: {card_bg}; border: 1px solid {card_border}; border-radius: 10px; padding: 1rem; margin-bottom: 1rem;">
                    <strong>{icon} Question {q_idx + 1}: {q['question']}</strong><br>
                    <span style="font-size: 0.95rem;">• <b>Your Answer:</b> {user_ans or '<i>Not answered</i>'}</span><br>
                    <span style="font-size: 0.95rem; color: #166534;">• <b>Correct Answer:</b> {correct_ans}</span><br>
                    <div style="margin-top: 0.5rem; padding-top: 0.5rem; border-top: 1px dashed {card_border}; font-size: 0.9rem; color: #374151;">
                        💡 <b>Explanation:</b> {q.get('explanation', 'No explanation provided.')}
                    </div>
                </div>
                """, unsafe_allow_html=True)


# =============================================================
# TAB 4: "ASK MY NOTES" AI TUTOR
# =============================================================
with tab_tutor:
    st.markdown("### 💬 'Ask My Notes' AI Tutor")
    st.caption("Engage in pedagogical dialogue with your notes. Switch tutor personas to gain new perspectives!")

    t_col1, t_col2 = st.columns([2, 1])
    with t_col1:
        tutor_mode = st.selectbox(
            "Tutor Persona & Teaching Strategy:",
            options=["Academic Tutor", "Feynman Technique", "Socratic Mentor", "Exam Prep Coach"],
            index=1,
            help="Feynman Technique explains like you are 10 using analogies; Socratic asks questions; Exam Coach gives mnemonics and test strategies."
        )
    with t_col2:
        st.write("")
        if st.button("🗑️ Clear Chat History", use_container_width=True):
            st.session_state.chat_history = [
                {"role": "assistant", "content": f"👋 Conversation reset. I am ready in **{tutor_mode}** mode. What would you like to explore?"}
            ]
            st.rerun()

    # Quick prompt suggestion pills
    st.markdown("##### ⚡ Quick Questions:")
    qp_cols = st.columns(4)
    quick_prompt = None
    with qp_cols[0]:
        if st.button("💡 Explain with an analogy", use_container_width=True):
            quick_prompt = "Explain the core mechanism in this study material using a simple, memorable everyday analogy."
    with qp_cols[1]:
        if st.button("⚠️ Common exam traps", use_container_width=True):
            quick_prompt = "What are the most frequent student misconceptions or exam traps for this topic?"
    with qp_cols[2]:
        if st.button("🧠 Give me a mnemonic", use_container_width=True):
            quick_prompt = "Create a catchy mnemonic or memory acronym to help me recall the key terms or stages."
    with qp_cols[3]:
        if st.button("🌍 Real-world application", use_container_width=True):
            quick_prompt = "How does this concept apply in real-world industry, modern science, or daily life?"

    st.markdown("---")

    # Render Chat History
    for msg in st.session_state.chat_history:
        avatar = "🎓" if msg["role"] == "assistant" else "🧑‍🎓"
        with st.chat_message(msg["role"], avatar=avatar):
            st.markdown(msg["content"])

    # Chat Input
    user_input = st.chat_input("Ask a question about your study material...")
    prompt_to_send = quick_prompt or user_input

    if prompt_to_send:
        # Append student message
        st.session_state.chat_history.append({"role": "user", "content": prompt_to_send})
        with st.chat_message("user", avatar="🧑‍🎓"):
            st.markdown(prompt_to_send)

        # Generate Tutor Response
        tutor = TutorChat(st.session_state.ai_engine)
        with st.chat_message("assistant", avatar="🎓"):
            with st.spinner(f"Consulting notes ({tutor_mode})..."):
                response_text = tutor.ask(
                    user_query=prompt_to_send,
                    study_context=st.session_state.study_text,
                    chat_history=st.session_state.chat_history,
                    mode=tutor_mode
                )
                st.markdown(response_text)
                st.session_state.chat_history.append({"role": "assistant", "content": response_text})


# =============================================================
# TAB 5: STUDY PLANNER & POMODORO TIMER
# =============================================================
with tab_planner:
    st.markdown("### ⏱️ Personalized Study Planner & Focus Pomodoro")

    plan_c1, plan_c2 = st.columns([1, 1])

    # Left: Timetable Generator
    with plan_c1:
        st.markdown("#### 📅 Exam Countdown & Spaced Schedule")
        today = datetime.date.today()
        exam_target_date = st.date_input("Target Exam Date:", value=today + datetime.timedelta(days=14), min_value=today + datetime.timedelta(days=1))
        hrs_per_day = st.slider("Dedicated Daily Study Hours:", min_value=1.0, max_value=8.0, value=2.5, step=0.5)
        study_intensity = st.select_slider("Preparation Style:", options=["Cram / Intensive", "Balanced Spaced", "Deep Mastery"], value="Balanced Spaced")
        
        if st.button("🗓️ Build Personalized Study Plan", type="primary", use_container_width=True):
            with st.spinner("Calculating optimal spaced retrieval intervals..."):
                plan_result = generate_study_plan(
                    topics=[st.session_state.active_doc_title, "Key Terminology Review", "Active Recall Drills", "Mock Exam Simulation"],
                    exam_date=exam_target_date,
                    daily_hours=hrs_per_day,
                    intensity=study_intensity,
                    ai_engine=st.session_state.ai_engine
                )
                st.session_state.study_plan = plan_result
                st.rerun()

        if st.session_state.study_plan:
            plan = st.session_state.study_plan
            st.markdown(plan["plan_markdown"])
            if "schedule_table" in plan:
                st.markdown("##### 📋 Day-by-Day Roadmap Table:")
                st.dataframe(plan["schedule_table"], use_container_width=True)

    # Right: Focus Pomodoro Clock & Ambient Environment
    with plan_c2:
        st.markdown("#### ⏳ Pomodoro Focus Station")
        st.caption("25-minute high-focus interval followed by 5-minute cognitive refresh.")
        
        timer_col1, timer_col2 = st.columns(2)
        with timer_col1:
            work_mins = st.selectbox("Focus Duration (min):", [25, 50, 15], index=0)
        with timer_col2:
            break_mins = st.selectbox("Break Duration (min):", [5, 10, 15], index=0)

        # Interactive HTML5/JS Pomodoro Timer
        pomodoro_html = f"""
        <div style="background: linear-gradient(135deg, #1e1b4b, #312e81); border-radius: 16px; padding: 2rem; color: white; text-align: center; box-shadow: 0 10px 20px rgba(0,0,0,0.2);">
            <div id="pomo-mode" style="text-transform: uppercase; letter-spacing: 2px; font-size: 0.9rem; color: #a5b4fc; font-weight: 700;">FOCUS SESSION</div>
            <div id="pomo-display" style="font-family: 'Courier New', monospace; font-size: 4rem; font-weight: 800; margin: 1rem 0; color: #ffffff;">{work_mins:02d}:00</div>
            
            <div style="display: flex; justify-content: center; gap: 10px; margin-top: 1rem;">
                <button onclick="startTimer()" style="background: #22c55e; color: white; border: none; padding: 10px 24px; border-radius: 8px; font-weight: bold; cursor: pointer; font-size: 1rem;">▶ Start</button>
                <button onclick="pauseTimer()" style="background: #f59e0b; color: white; border: none; padding: 10px 24px; border-radius: 8px; font-weight: bold; cursor: pointer; font-size: 1rem;">⏸ Pause</button>
                <button onclick="resetTimer()" style="background: #ef4444; color: white; border: none; padding: 10px 24px; border-radius: 8px; font-weight: bold; cursor: pointer; font-size: 1rem;">🔄 Reset</button>
            </div>
            
            <script>
                let workTime = {work_mins} * 60;
                let breakTime = {break_mins} * 60;
                let timeLeft = workTime;
                let isRunning = false;
                let isBreak = false;
                let timerInterval = null;

                function updateDisplay() {{
                    let mins = Math.floor(timeLeft / 60);
                    let secs = timeLeft % 60;
                    document.getElementById('pomo-display').innerText = 
                        (mins < 10 ? "0" : "") + mins + ":" + (secs < 10 ? "0" : "") + secs;
                }}

                function startTimer() {{
                    if (!isRunning) {{
                        isRunning = true;
                        timerInterval = setInterval(() => {{
                            if (timeLeft > 0) {{
                                timeLeft--;
                                updateDisplay();
                            }} else {{
                                clearInterval(timerInterval);
                                isRunning = false;
                                isBreak = !isBreak;
                                timeLeft = isBreak ? breakTime : workTime;
                                document.getElementById('pomo-mode').innerText = isBreak ? "BREAK TIME ☕" : "FOCUS SESSION 🧠";
                                document.getElementById('pomo-mode').style.color = isBreak ? "#34d399" : "#a5b4fc";
                                alert(isBreak ? "Pomodoro Finished! Take a well-earned break!" : "Break is over! Time to focus!");
                                updateDisplay();
                            }}
                        }}, 1000);
                    }}
                }}

                function pauseTimer() {{
                    isRunning = false;
                    clearInterval(timerInterval);
                }}

                function resetTimer() {{
                    isRunning = false;
                    clearInterval(timerInterval);
                    isBreak = false;
                    timeLeft = workTime;
                    document.getElementById('pomo-mode').innerText = "FOCUS SESSION";
                    document.getElementById('pomo-mode').style.color = "#a5b4fc";
                    updateDisplay();
                }}
            </script>
        </div>
        """
        st.components.v1.html(pomodoro_html, height=270)

        # Log Pomodoro Button
        if st.button("✅ Log Completed Pomodoro Session", use_container_width=True):
            st.session_state.pomodoro_count += 1
            st.success(f"Session logged! You have completed {st.session_state.pomodoro_count} pomodoros today ({st.session_state.pomodoro_count * 25} focused minutes).")

        st.markdown("##### 🎧 Ambient Study Audio (Synthesized Brown Noise)")
        # Native Web Audio API ambient brown noise generator
        ambient_html = """
        <div style="background: rgba(243, 244, 246, 0.8); border: 1px solid #d1d5db; border-radius: 12px; padding: 1rem; text-align: center;">
            <p style="font-size: 0.9rem; margin-bottom: 0.5rem; color: #4b5563;">Calming white/brown noise for deep immersion:</p>
            <button id="noise-btn" onclick="toggleNoise()" style="background: #4f46e5; color: white; border: none; padding: 8px 18px; border-radius: 6px; font-weight: 600; cursor: pointer;">
                🔊 Play Focus Ambient Sound
            </button>
            <script>
                let audioCtx = null;
                let noiseNode = null;
                let isPlayingNoise = false;

                function toggleNoise() {
                    const btn = document.getElementById('noise-btn');
                    if (!isPlayingNoise) {
                        audioCtx = new (window.AudioContext || window.webkitAudioContext)();
                        const bufferSize = audioCtx.sampleRate * 2;
                        const noiseBuffer = audioCtx.createBuffer(1, bufferSize, audioCtx.sampleRate);
                        const output = noiseBuffer.getChannelData(0);
                        let lastOut = 0.0;
                        for (let i = 0; i < bufferSize; i++) {
                            let white = Math.random() * 2 - 1;
                            output[i] = (lastOut + (0.02 * white)) / 1.02;
                            lastOut = output[i];
                            output[i] *= 3.5;
                        }
                        noiseNode = audioCtx.createBufferSource();
                        noiseNode.buffer = noiseBuffer;
                        noiseNode.loop = true;
                        
                        const gainNode = audioCtx.createGain();
                        gainNode.gain.value = 0.15;
                        noiseNode.connect(gainNode);
                        gainNode.connect(audioCtx.destination);
                        
                        noiseNode.start(0);
                        isPlayingNoise = true;
                        btn.innerText = "🔇 Stop Ambient Sound";
                        btn.style.background = "#dc2626";
                    } else {
                        if (noiseNode) {
                            noiseNode.stop();
                            noiseNode.disconnect();
                        }
                        if (audioCtx) {
                            audioCtx.close();
                        }
                        isPlayingNoise = false;
                        btn.innerText = "🔊 Play Focus Ambient Sound";
                        btn.style.background = "#4f46e5";
                    }
                }
            </script>
        </div>
        """
        st.components.v1.html(ambient_html, height=130)


# =============================================================
# TAB 6: PROGRESS ANALYTICS & EXPORT STUDY PACK
# =============================================================
with tab_analytics:
    st.markdown("### 📊 Progress Analytics & Comprehensive Study Pack")

    col_a1, col_a2 = st.columns([1, 1])

    with col_a1:
        st.markdown("#### 🧠 Flashcard Leitner Mastery Distribution")
        deck_stats = FlashcardDeck(st.session_state.flashcards).get_stats()
        chart_donut = StudyAnalytics.create_flashcard_donut_chart(deck_stats)
        if chart_donut:
            st.plotly_chart(chart_donut, use_container_width=True)
        else:
            st.info("Generate or review flashcards in Tab 2 to visualize mastery distribution.")

    with col_a2:
        st.markdown("#### 📈 Practice Quiz Score Trajectory")
        chart_quiz = StudyAnalytics.create_quiz_history_chart(st.session_state.quiz_history)
        if chart_quiz:
            st.plotly_chart(chart_quiz, use_container_width=True)
        else:
            st.info("Take a practice quiz in Tab 3 to record and graph performance trends.")

    st.markdown("---")
    st.markdown("#### 📦 Export Complete Study Pack")
    st.caption("Package your summary, key definitions, flashcards deck, and quiz into a single markdown file ready for offline study or printing.")

    study_pack_md = StudyAnalytics.build_study_pack_markdown(
        title=st.session_state.active_doc_title,
        summary_data=st.session_state.summary_data or {"tldr": "N/A", "executive": st.session_state.study_text[:400]},
        flashcards=st.session_state.flashcards,
        quiz=st.session_state.quiz_data
    )

    p_col1, p_col2 = st.columns([1, 2])
    with p_col1:
        st.download_button(
            "📥 Download Complete Study Pack (.MD)",
            data=study_pack_md,
            file_name=f"Study_Pack_{st.session_state.active_doc_title.replace(' ', '_')}.md",
            mime="text/markdown",
            type="primary",
            use_container_width=True
        )
    with p_col2:
        with st.expander("👁️ Preview Study Pack Output"):
            st.markdown(study_pack_md)
