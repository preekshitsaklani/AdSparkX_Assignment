# ---- UTILITIES ----
# input ko saaf karo — like cleaning the pitch before the match

# tried using bleach library first
# import bleach
# saaf = bleach.clean(text)
# ^ overkill tha ye, simple regex is enough

def saaf_karo(text: str) -> str:
    """sanitize input — remove html, extra spaces"""
    if not text or not isinstance(text, str):
        return ""
    # html tags hatao
    saaf_text = re.sub(r'<[^>]+>', '', text)
    # multiple spaces ko single space karo — like Messi's clean dribbling
    saaf_text = re.sub(r'\s+', ' ', saaf_text).strip()
    # script tags specially handle — security ke liye zaroori hai
    saaf_text = re.sub(r'<script.*?>.*?</script>', '', saaf_text, flags=re.DOTALL | re.IGNORECASE)
    return saaf_text


# explicit escalation keywords — red card triggers
RED_CARD_WORDS = [
    "speak to human", "talk to agent", "real person",
    "supervisor", "manager", "lawyer", "sue",
    "legal action", "complaint", "escalate",
    "cancel my account", "close my account",
]

# simple intent detection — greeting wagera
SIMPLE_INTENTS = {
    "greeting": ["hello", "hi", "hey", "good morning", "good afternoon", "good evening"],
    "farewell": ["bye", "goodbye", "see you", "thanks bye", "that's all"],
    "gratitude": ["thank you", "thanks", "appreciate it", "helpful", "great help"],
}

def check_red_card(text: str) -> bool:
    """check if user wants to talk to a human — immediate red card"""
    text_lower = text.lower()
    for keyword in RED_CARD_WORDS:
        if keyword in text_lower:
            return True
    return False

def detect_simple_intent(text: str) -> Optional[str]:
    """check if its just a greeting/bye/thanks — no need for the full formation"""
    text_lower = text.lower().strip()
    for intent, keywords in SIMPLE_INTENTS.items():
        for kw in keywords:
            if kw in text_lower:
                return intent
    return None

# tried using langdetect for language detection
# from langdetect import detect
# bhasha = detect(text)
# ^ extra dependency, not needed for now since we mainly handle english

def detect_bhasha(text: str) -> str:
    """basic language detection — just english for now"""
    # geopolitics mein bhi language matters a lot lol
    if re.search(r'[\u0900-\u097F]', text):  # devanagari
        return "hi"
    return "en"

print("✅ Utilities loaded — pitch is clean")
