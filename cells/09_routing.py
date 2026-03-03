# ---- ROUTING EDGES ----
# the tactical decisions — like a chess opening strategy

def route_after_persona(state: dict) -> str:
    """decide where to go after persona detection — chess opening"""
    # check if escalation needed
    if state.get("should_escalate"):
        return "escalation"

    route = state.get("route_decision", "needs_analysis")

    # simple intents go to direct response
    if route.startswith("simple_"):
        return "direct_response"

    # everything else goes to KB retrieval
    return "kb_retrieval"


def route_after_quality(state: dict) -> str:
    """decide after quality check — VAR decision"""
    # if escalation was triggered
    if state.get("should_escalate"):
        return "escalation"

    score = state.get("quality_score", 0)
    retry = state.get("retry_count", 0)

    # passed quality gate — GOAL!
    if score >= RONALDO_CONFIG["quality_threshold"]:
        return "output"

    # can still retry — VAR is still reviewing
    if retry <= RONALDO_CONFIG["max_retries"]:
        return "response_generation"

    # exhausted retries — red card, escalate
    return "escalation"


print("Routing edges defined — tactical plan is set")
