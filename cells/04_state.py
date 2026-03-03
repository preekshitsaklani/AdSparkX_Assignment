# ---- AGENT STATE ----
# pehle pydantic use kiya tha but wo bahut complex hai for this
# from pydantic import BaseModel, Field
# class AgentState(BaseModel):
#     current_user_message: str = Field(default="")
#     ... bahut fields the, headache ho gaya

class AgentState(TypedDict, total=False):
    current_user_message: str
    saaf_message: str  # cleaned/sanitized message
    conversation_history: List[Dict[str, str]]
    detected_persona: str  # TECHNICAL_EXPERT | FRUSTRATED_USER | BUSINESS_EXECUTIVE | GENERAL_USER
    persona_confidence: float
    kb_results: List[Dict[str, Any]]
    kb_query: str
    jawab: str  # the final response — jawab means answer
    quality_score: float
    quality_feedback: str
    retry_count: int
    should_escalate: bool
    escalation_wajah: str  # wajah = reason
    escalation_priority: str
    escalation_department: str
    escalation_summary: str
    is_resolved: bool
    route_decision: str
    bhasha: str  # language detected

# helper functions — like utility players on the bench
def make_fresh_state(user_msg: str) -> dict:
    """naya state banao for a new conversation"""
    return {
        "current_user_message": user_msg,
        "saaf_message": "",
        "conversation_history": [],
        "detected_persona": "GENERAL_USER",
        "persona_confidence": 0.0,
        "kb_results": [],
        "kb_query": "",
        "jawab": "",
        "quality_score": 0.0,
        "quality_feedback": "",
        "retry_count": 0,
        "should_escalate": False,
        "escalation_wajah": "",
        "escalation_priority": "medium",
        "escalation_department": "general_support",
        "escalation_summary": "",
        "is_resolved": False,
        "route_decision": "",
        "bhasha": "en",
    }

# persona profiles — like player positions
CHESS_PERSONAS = {
    "TECHNICAL_EXPERT": {
        "tone": "precise, code-heavy, no fluff",
        "kb_tier": "technical_deep",
        "max_tokens": 2048,
        "temp": 0.3,  # low temperature = more precise, like a chess grandmaster
    },
    "FRUSTRATED_USER": {
        "tone": "empathy-first, simple steps, offer escalation",
        "kb_tier": "simplified",
        "max_tokens": 1024,
        "temp": 0.7,
    },
    "BUSINESS_EXECUTIVE": {
        "tone": "concise metrics, executive summary, bold KPIs",
        "kb_tier": "executive_summary",
        "max_tokens": 800,
        "temp": 0.5,
    },
    "GENERAL_USER": {
        "tone": "warm, patient, step-by-step",
        "kb_tier": "simplified",
        "max_tokens": 1200,
        "temp": 0.7,
    },
}

print("✅ State model and persona profiles ready")
