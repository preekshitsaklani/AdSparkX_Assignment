# ---- GRAPH ASSEMBLY ----
# putting the formation together — like setting up before kickoff
# this is where langgraph magic happens

# tried using langchain's AgentExecutor first
# from langchain.agents import AgentExecutor
# agent = AgentExecutor.from_agent_and_tools(agent=..., tools=[...])
# ^ too rigid, langgraph gives more control like a custom formation

# the football formation — our state graph
formation = StateGraph(AgentState)

# add all players (nodes) to the formation
formation.add_node("intake", intake_node)
formation.add_node("persona_detection", persona_detection_node)
formation.add_node("kb_retrieval", kb_retrieval_node)
formation.add_node("response_generation", response_generation_node)
formation.add_node("direct_response", direct_response_node)
formation.add_node("quality_gate", quality_gate_node)
formation.add_node("escalation", escalation_node)
formation.add_node("output", output_node)

# set the entry point — kickoff!
formation.set_entry_point("intake")

# linear edges — the basic passing lanes
formation.add_edge("intake", "persona_detection")

# conditional edge after persona — the chess decision
formation.add_conditional_edges(
    "persona_detection",
    route_after_persona,
    {
        "escalation": "escalation",
        "direct_response": "direct_response",
        "kb_retrieval": "kb_retrieval",
    }
)

# KB -> Response Generation
formation.add_edge("kb_retrieval", "response_generation")

# Response Gen -> Quality Gate
formation.add_edge("response_generation", "quality_gate")

# Direct Response -> Quality Gate
formation.add_edge("direct_response", "quality_gate")

# conditional edge after quality — VAR decision
formation.add_conditional_edges(
    "quality_gate",
    route_after_quality,
    {
        "output": "output",
        "response_generation": "response_generation",
        "escalation": "escalation",
    }
)

# end nodes — final whistle
formation.add_edge("output", END)
formation.add_edge("escalation", END)

# compile the graph — like the referee blowing the starting whistle
# tried using .compile(checkpointer=...) for memory
# but its simpler without checkpointer for now
agent_graph = formation.compile()

print("Agent graph compiled — formation is ready!")
print("   Nodes: intake -> persona -> [route] -> kb/direct/escalate -> quality -> [route] -> output/retry/escalate")
