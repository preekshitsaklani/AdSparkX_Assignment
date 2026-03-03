# ---- GRAPH NODES ----
# each node is like a player on the team with a specific role

# tried using function calling first
# from langchain.tools import tool
# @tool
# def detect_persona(msg): ...
# ^ function calling was too complex, raw LLM calls are simpler

# NODE 1: Intake — the goalkeeper, first line of defense
def intake_node(state: dict) -> dict:
    messi_logger.info("Intake node — cleaning the message")

    raw_msg = state.get("current_user_message", "")
    saaf = saaf_karo(raw_msg)
    bhasha = detect_bhasha(raw_msg)

    # check for immediate red card (escalation keywords)
    needs_red_card = check_red_card(saaf)

    # check for simple intent
    simple = detect_simple_intent(saaf)

    updates = {
        "saaf_message": saaf,
        "bhasha": bhasha,
    }

    if needs_red_card:
        updates["should_escalate"] = True
        updates["escalation_wajah"] = "Customer explicitly requested human agent"
        updates["route_decision"] = "escalation"
    elif simple:
        updates["route_decision"] = f"simple_{simple}"
    else:
        updates["route_decision"] = "needs_analysis"

    return updates


# NODE 2: Persona Detection — the VAR check, analyzing the player
def persona_detection_node(state: dict) -> dict:
    messi_logger.info("Persona detection — VAR reviewing the play")

    saaf = state.get("saaf_message", "")

    # if already marked for escalation, skip detection
    if state.get("should_escalate"):
        return {}

    # if simple intent, default persona is fine
    if state.get("route_decision", "").startswith("simple_"):
        return {"detected_persona": "GENERAL_USER", "persona_confidence": 0.9}

    try:
        prompt = PERSONA_DETECTION_PROMPT.format(message=saaf)
        ai_msg = goalkeeper.invoke([HumanMessage(content=prompt)])
        response_text = ai_msg.content.strip()

        # parse the JSON — sometimes LLM adds extra text around it
        # ye bahut annoying hai, tried regex first
        # match = re.search(r'\{.*\}', response_text, re.DOTALL)
        # ^ ye kaam nahi kar raha tha properly

        # clean up response to get just JSON
        json_start = response_text.find('{')
        json_end = response_text.rfind('}') + 1
        if json_start >= 0 and json_end > json_start:
            json_str = response_text[json_start:json_end]
            parsed = json.loads(json_str)
        else:
            # fallback — treat as general user
            parsed = {"persona": "GENERAL_USER", "confidence": 0.5, "reasoning": "could not parse"}

        detected = parsed.get("persona", "GENERAL_USER")
        confidence = float(parsed.get("confidence", 0.5))

        # validate persona name
        valid_personas = ["TECHNICAL_EXPERT", "FRUSTRATED_USER", "BUSINESS_EXECUTIVE", "GENERAL_USER"]
        if detected not in valid_personas:
            detected = "GENERAL_USER"
            confidence = 0.5

        messi_logger.info(f"   Detected: {detected} (confidence: {confidence})")

        return {
            "detected_persona": detected,
            "persona_confidence": confidence,
        }

    except Exception as e:
        messi_logger.error(f"Persona detection failed: {e}")
        return {"detected_persona": "GENERAL_USER", "persona_confidence": 0.3}


# NODE 3: KB Retrieval — fetching tactical info from the video room
def kb_retrieval_node(state: dict) -> dict:
    messi_logger.info("KB Retrieval — checking the tactical notebook")

    saaf = state.get("saaf_message", "")
    persona = state.get("detected_persona", "GENERAL_USER")

    # get the right content tier based on persona
    tier = CHESS_PERSONAS.get(persona, {}).get("kb_tier", "simplified")

    # first try to reformulate the query using LLM for better search
    # like a chess player thinking 3 moves ahead
    try:
        reformulate_prompt = f"Rewrite this customer support query as a concise search query for a knowledge base. Only output the search query, nothing else.\n\nQuery: {saaf}"
        reformulated = goalkeeper.invoke([HumanMessage(content=reformulate_prompt)])
        search_query = reformulated.content.strip()
    except:
        search_query = saaf  # fallback to original

    # search KB
    results = search_kb(search_query, content_tier=tier, top_k=3)

    kuch_mila = len(results) > 0  # did we find anything?

    messi_logger.info(f"   Found {len(results)} results (tier: {tier})")

    return {
        "kb_results": results,
        "kb_query": search_query,
    }


# NODE 4: Response Generation — the striker, scoring the goal
def response_generation_node(state: dict) -> dict:
    messi_logger.info("Response generation — time to score!")

    saaf = state.get("saaf_message", "")
    persona = state.get("detected_persona", "GENERAL_USER")
    kb_results = state.get("kb_results", [])
    history = state.get("conversation_history", [])
    quality_feedback = state.get("quality_feedback", "")

    # prepare KB context
    if kb_results:
        kb_context = "\n---\n".join([r["text"] for r in kb_results])
    else:
        kb_context = "No specific knowledge base articles found. Use general knowledge."

    # prepare history string
    if history:
        history_str = "\n".join([f"{h['role']}: {h['content']}" for h in history[-5:]])
    else:
        history_str = "No previous conversation."

    # get persona-specific prompt
    prompt_template = RESPONSE_PROMPTS.get(persona, RESPONSE_PROMPTS["GENERAL_USER"])
    prompt = prompt_template.format(
        kb_context=kb_context,
        history=history_str,
        message=saaf,
    )

    # if this is a retry, add quality feedback
    if quality_feedback:
        prompt += f"\n\nPREVIOUS ATTEMPT FEEDBACK (improve on this):\n{quality_feedback}"

    try:
        # use persona-specific temperature — like adjusting the difficulty level in a chess engine
        persona_config = CHESS_PERSONAS.get(persona, CHESS_PERSONAS["GENERAL_USER"])

        # temporarily adjust goalkeeper's temperature
        # tried making separate LLM instances per persona first
        # goalkeeper_tech = ChatNVIDIA(model=..., temperature=0.3)
        # goalkeeper_frustrated = ChatNVIDIA(model=..., temperature=0.7)
        # ^ too many instances, waste of memory

        ai_msg = goalkeeper.invoke([
            SystemMessage(content=f"Respond with the tone: {persona_config['tone']}"),
            HumanMessage(content=prompt)
        ])

        jawab = ai_msg.content.strip()
        messi_logger.info(f"   Generated response ({len(jawab)} chars)")

        return {"jawab": jawab}

    except Exception as e:
        messi_logger.error(f"Response generation failed: {e}")
        return {
            "jawab": "I apologize, but I'm having trouble generating a response. Let me connect you with a team member who can help.",
            "should_escalate": True,
            "escalation_wajah": f"Response generation error: {str(e)}",
        }


# NODE 5: Direct Response — quick plays for simple situations
def direct_response_node(state: dict) -> dict:
    messi_logger.info("Direct response — quick pass")

    route = state.get("route_decision", "")

    # template responses — no need to bother the LLM for these
    # like taking a free kick instead of building up from the back
    templates = {
        "simple_greeting": "Hello! Welcome to our support team. How can I help you today?",
        "simple_farewell": "Thank you for contacting us! Have a great day! If you need anything else, we're always here.",
        "simple_gratitude": "You're welcome! I'm glad I could help. Is there anything else you'd like to know?",
    }

    jawab = templates.get(route, "Hi there! How can I assist you?")

    return {"jawab": jawab, "quality_score": 0.95}  # pre-approved quality for templates


# NODE 6: Quality Gate — the referee, checking if the goal is valid
def quality_gate_node(state: dict) -> dict:
    messi_logger.info("Quality gate — referee reviewing the goal")

    jawab = state.get("jawab", "")
    persona = state.get("detected_persona", "GENERAL_USER")
    saaf = state.get("saaf_message", "")
    kb_results = state.get("kb_results", [])

    # if already high quality (direct response), skip
    if state.get("quality_score", 0) >= 0.9:
        messi_logger.info("   Pre-approved quality — skipping check")
        return {}

    kb_context = "\n---\n".join([r["text"] for r in kb_results]) if kb_results else "No KB context"

    try:
        prompt = QUALITY_GATE_PROMPT.format(
            persona=persona,
            query=saaf,
            kb_context=kb_context,
            response=jawab,
        )

        ai_msg = goalkeeper.invoke([HumanMessage(content=prompt)])
        response_text = ai_msg.content.strip()

        # parse JSON
        json_start = response_text.find('{')
        json_end = response_text.rfind('}') + 1

        if json_start >= 0 and json_end > json_start:
            scores = json.loads(response_text[json_start:json_end])
        else:
            # if parsing fails, give it a passing score
            scores = {"overall_score": 0.8, "feedback": "Could not parse quality scores"}

        overall = float(scores.get("overall_score", 0.8))

        # --- HARDCODED CHECKS (even the LLM can miss these) ---

        # frustrated user MUST start with empathy
        if persona == "FRUSTRATED_USER":
            pehla_line = jawab.split('.')[0].lower() if jawab else ""
            empathy_words = ["sorry", "apologize", "hear", "understand", "acknowledge"]
            has_empathy = any(w in pehla_line for w in empathy_words)
            if not has_empathy:
                # penalize tone score — faaltu response without empathy
                tone_score = scores.get("tone_score", 0.7)
                scores["tone_score"] = tone_score * 0.5
                # recalculate overall
                overall = (
                    float(scores.get("hallucination_score", 0.8)) * 0.35 +
                    float(scores.get("tone_score", 0.5)) * 0.25 +
                    float(scores.get("completeness_score", 0.7)) * 0.30 +
                    float(scores.get("safety_score", 0.9)) * 0.10
                )
                messi_logger.info("   Frustrated user penalty — no empathy detected")

        # technical expert should NOT have fluff empathy
        if persona == "TECHNICAL_EXPERT":
            faaltu_empathy = ["i understand your frustration", "i can see how frustrating"]
            for phrase in faaltu_empathy:
                if phrase in jawab.lower():
                    scores["tone_score"] = float(scores.get("tone_score", 0.7)) * 0.3
                    overall = (
                        float(scores.get("hallucination_score", 0.8)) * 0.35 +
                        float(scores.get("tone_score", 0.5)) * 0.25 +
                        float(scores.get("completeness_score", 0.7)) * 0.30 +
                        float(scores.get("safety_score", 0.9)) * 0.10
                    )
                    messi_logger.info("   Tech expert penalty — unnecessary empathy fluff")
                    break

        paas_hua = overall >= RONALDO_CONFIG["quality_threshold"]  # did it pass?
        retry = state.get("retry_count", 0)

        messi_logger.info(f"   Score: {overall:.2f} | Pass: {paas_hua} | Retry: {retry}")

        updates = {
            "quality_score": overall,
            "quality_feedback": scores.get("feedback", ""),
        }

        if not paas_hua:
            if retry < RONALDO_CONFIG["max_retries"]:
                updates["retry_count"] = retry + 1
            else:
                updates["should_escalate"] = True
                updates["escalation_wajah"] = f"Quality gate failed after {retry} retries (score: {overall:.2f})"

        return updates

    except Exception as e:
        messi_logger.error(f"Quality gate error: {e}")
        return {"quality_score": 0.7, "quality_feedback": f"Quality check error: {str(e)}"}


# NODE 7: Escalation — red card, substituting to human agent
def escalation_node(state: dict) -> dict:
    messi_logger.info("Escalation — substituting in a human agent")

    saaf = state.get("saaf_message", "")
    persona = state.get("detected_persona", "GENERAL_USER")
    history = state.get("conversation_history", [])
    wajah = state.get("escalation_wajah", "Unknown reason")

    # determine department — like choosing which substitute player to bring on
    # geopolitics mein bhi sahi department mein bhejte hain lol
    department = "general_support"
    priority = "medium"

    msg_lower = saaf.lower()
    if any(w in msg_lower for w in ["bill", "charge", "refund", "payment", "invoice"]):
        department = "billing"
    elif any(w in msg_lower for w in ["hack", "breach", "unauthorized", "security", "password"]):
        department = "security"
        priority = "high"
    elif any(w in msg_lower for w in ["api", "sdk", "error", "bug", "crash"]):
        department = "technical"

    # frustrated users get higher priority — like VAR checking a potential penalty
    if persona == "FRUSTRATED_USER":
        priority = "high"
    elif persona == "BUSINESS_EXECUTIVE":
        priority = "high"  # executives = VIP

    # generate handoff summary using LLM
    try:
        history_str = "\n".join([f"{h['role']}: {h['content']}" for h in history[-5:]]) if history else "No history"

        prompt = ESCALATION_SUMMARY_PROMPT.format(
            history=history_str,
            message=saaf,
            persona=persona,
            reason=wajah,
        )
        ai_msg = goalkeeper.invoke([HumanMessage(content=prompt)])
        summary = ai_msg.content.strip()
    except Exception as e:
        summary = f"Customer ({persona}) needs help. Issue: {saaf}. Reason for escalation: {wajah}"

    # the handoff message
    dept_display = department.replace('_', ' ').title()
    escalation_jawab = f"""**Transferring you to a human agent**

I understand you need additional assistance. I'm connecting you with our **{dept_display}** team.

**What happens next:**
- A support agent will be with you shortly
- Priority: **{priority.upper()}**
- Your conversation history has been shared for a seamless handoff

Thank you for your patience!"""

    messi_logger.info(f"   Department: {department} | Priority: {priority}")

    return {
        "jawab": escalation_jawab,
        "should_escalate": True,
        "escalation_department": department,
        "escalation_priority": priority,
        "escalation_summary": summary,
        "is_resolved": False,
    }


# NODE 8: Output — final whistle, game over
def output_node(state: dict) -> dict:
    messi_logger.info("Output node — final whistle!")

    jawab = state.get("jawab", "")
    saaf = state.get("saaf_message", "")

    # update conversation history
    history = list(state.get("conversation_history", []))
    history.append({"role": "user", "content": saaf})
    history.append({"role": "assistant", "content": jawab})

    return {
        "conversation_history": history,
        "is_resolved": True,
    }


print("All 8 nodes ready — full squad assembled")
