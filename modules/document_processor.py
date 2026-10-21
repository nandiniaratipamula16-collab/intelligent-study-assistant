"""
Document processing module for loading, parsing, and extracting structured content
from various file formats (PDF, DOCX, TXT, MD) and raw text input.
"""

import io
import re
from typing import Dict, Any, List, Optional

def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract clean text from a PDF file byte stream using pypdf."""
    text_content = []
    try:
        import pypdf
        reader = pypdf.PdfReader(io.BytesIO(file_bytes))
        for page_idx, page in enumerate(reader.pages):
            page_text = page.extract_text()
            if page_text:
                text_content.append(page_text.strip())
        return "\n\n".join(text_content)
    except Exception as e:
        return f"Error extracting PDF: {str(e)}"

def extract_text_from_docx(file_bytes: bytes) -> str:
    """Extract text from a DOCX file byte stream."""
    try:
        import docx
        doc = docx.Document(io.BytesIO(file_bytes))
        paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
        return "\n\n".join(paragraphs)
    except Exception as e:
        return f"Error extracting DOCX: {str(e)}"

def extract_text_from_uploaded_file(uploaded_file) -> str:
    """Detect file type and extract text content safely."""
    if uploaded_file is None:
        return ""
    
    file_bytes = uploaded_file.getvalue()
    filename = uploaded_file.name.lower()

    if filename.endswith(".pdf"):
        return extract_text_from_pdf(file_bytes)
    elif filename.endswith(".docx"):
        return extract_text_from_docx(file_bytes)
    elif filename.endswith((".txt", ".md", ".csv", ".json")):
        try:
            return file_bytes.decode("utf-8")
        except UnicodeDecodeError:
            try:
                return file_bytes.decode("latin-1")
            except Exception as e:
                return f"Error decoding text file: {str(e)}"
    else:
        # Fallback to UTF-8 text decoding
        try:
            return file_bytes.decode("utf-8", errors="ignore")
        except Exception as e:
            return f"Unsupported file type: {filename}. {str(e)}"

def clean_and_normalize_text(text: str) -> str:
    """Clean up whitespace, anomalous characters, and excessive line breaks."""
    if not text:
        return ""
    # Standardize line endings
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    # Replace multiple blank lines with max two
    text = re.sub(r'\n{3,}', '\n\n', text)
    # Trim leading/trailing whitespace
    return text.strip()

def compute_text_metrics(text: str) -> Dict[str, Any]:
    """Calculate key analytical metrics for the text."""
    if not text:
        return {
            "char_count": 0,
            "word_count": 0,
            "sentence_count": 0,
            "paragraph_count": 0,
            "reading_time_min": 0,
            "flesch_reading_ease": 0.0,
            "difficulty_label": "N/A"
        }
    
    clean_text = clean_and_normalize_text(text)
    words = re.findall(r'\b[A-Za-z0-9\'-]+\b', clean_text)
    word_count = len(words)
    
    # Sentences split by punctuation
    sentences = [s.strip() for s in re.split(r'[.!?]+', clean_text) if s.strip()]
    sentence_count = max(1, len(sentences))
    
    # Paragraphs split by double line breaks
    paragraphs = [p.strip() for p in clean_text.split('\n\n') if p.strip()]
    paragraph_count = max(1, len(paragraphs))
    
    # Estimated reading time (average 200 words per minute)
    reading_time_min = round(max(0.5, word_count / 200), 1) if word_count > 0 else 0
    
    # Syllable count approximation for Flesch Reading Ease
    total_syllables = sum(_count_syllables(w) for w in words)
    if word_count > 0 and sentence_count > 0:
        # Flesch Reading Ease formula: 206.835 - 1.015 * (total_words / total_sentences) - 84.6 * (total_syllables / total_words)
        asl = word_count / sentence_count
        asw = total_syllables / word_count
        fre = 206.835 - (1.015 * asl) - (84.6 * asw)
        fre = max(0.0, min(100.0, fre))
        
        if fre >= 80:
            difficulty = "Easy / Elementary"
        elif fre >= 60:
            difficulty = "Standard / High School"
        elif fre >= 40:
            difficulty = "Fairly Difficult / College"
        else:
            difficulty = "Dense / Academic Graduate"
    else:
        fre = 0.0
        difficulty = "N/A"

    return {
        "char_count": len(clean_text),
        "word_count": word_count,
        "sentence_count": sentence_count,
        "paragraph_count": paragraph_count,
        "reading_time_min": reading_time_min,
        "flesch_reading_ease": round(fre, 1),
        "difficulty_label": difficulty
    }

def _count_syllables(word: str) -> int:
    """Rough syllable count heuristic for English words."""
    word = word.lower().strip()
    if len(word) <= 3:
        return 1
    # Remove trailing 'e'
    if word.endswith('e') and not word.endswith('le'):
        word = word[:-1]
    count = len(re.findall(r'[aeiouy]+', word))
    return max(1, count)

def chunk_text(text: str, max_chunk_size: int = 1500, overlap: int = 200) -> List[str]:
    """Break long documents into overlapping segments for context window management."""
    if not text:
        return []
    
    paragraphs = text.split("\n\n")
    chunks = []
    current_chunk = []
    current_length = 0

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        para_len = len(para)
        if current_length + para_len > max_chunk_size and current_chunk:
            chunks.append("\n\n".join(current_chunk))
            current_chunk = [para]
            current_length = para_len
        else:
            current_chunk.append(para)
            current_length += para_len

    if current_chunk:
        chunks.append("\n\n".join(current_chunk))
    
    return chunks
