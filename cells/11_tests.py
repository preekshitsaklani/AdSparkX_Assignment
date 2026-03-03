# ---- INTERACTIVE TESTING ----
# time to play some matches!

def run_test(test_name: str, message: str):
    """run a test case — like playing a practice match"""
    print(f"\n{'='*60}")
    print(f"TEST: {test_name}")
    print(f"{'='*60}")
    print(f"Input: {message}")
    print(f"-" * 60)

    # create fresh state
    initial_state = make_fresh_state(message)

    try:
        # run the graph
        result = agent_graph.invoke(initial_state)

        print(f"Persona: {result.get('detected_persona', 'N/A')} (confidence: {result.get('persona_confidence', 0):.2f})")
        print(f"Quality: {result.get('quality_score', 0):.2f}")
        print(f"Escalated: {result.get('should_escalate', False)}")

        if result.get("should_escalate"):
            print(f"   Department: {result.get('escalation_department', 'N/A')}")
            print(f"   Priority: {result.get('escalation_priority', 'N/A')}")
            print(f"   Reason: {result.get('escalation_wajah', 'N/A')}")

        print(f"\nResponse:")
        print(result.get("jawab", "No response generated"))
        print(f"{'='*60}")
        return result

    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()
        return None


# ---- TEST CASES ----
# 5 practice matches to test our formation

print("\nRunning test suite...\n")

# Match 1: Technical Expert — the chess grandmaster
run_test(
    "Technical Expert Query",
    "I'm getting a 429 Too Many Requests error when calling the /v2/data endpoint with my OAuth2 PKCE flow. I've implemented exponential backoff but the Retry-After header shows inconsistent values. Using SDK v3.2.1. What's the correct implementation?"
)

# Match 2: Frustrated User — needs empathy first
run_test(
    "Frustrated User",
    "THIS IS RIDICULOUS!!! I've been charged TWICE for my subscription and nobody is helping me!! I want my money back RIGHT NOW or I'm cancelling everything!!!"
)

# Match 3: Business Executive — wants metrics and summary
run_test(
    "Business Executive",
    "I need the latest SLA compliance report for our enterprise account. We have a board meeting next week and I need to present the ROI of this platform investment."
)

# Match 4: General User — needs patient help
run_test(
    "General User",
    "Hi, how do I reset my password? I can't seem to find where to do it."
)

# Match 5: Escalation Request — immediate red card
run_test(
    "Escalation Request",
    "I need to speak to a human agent right now. The AI is not understanding my issue and I want to talk to your supervisor."
)

print("\nAll test matches completed!")
