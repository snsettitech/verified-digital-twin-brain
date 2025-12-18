import os
from typing import Annotated, TypedDict, List, Dict, Any, Union
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage, ToolMessage
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from modules.tools import get_retrieval_tool, get_cloud_tools

class TwinState(TypedDict):
    """
    State for the Digital Twin reasoning graph.
    """
    messages: Annotated[List[BaseMessage], add_messages]
    twin_id: str
    confidence_score: float
    citations: List[str]

def create_twin_agent(twin_id: str, system_prompt_override: str = None):
    # Initialize the LLM
    api_key = os.getenv("OPENAI_API_KEY")
    # Using a model that supports tool calling well
    llm = ChatOpenAI(model="gpt-4-turbo-preview", api_key=api_key, temperature=0, streaming=True)
    
    # Setup tools
    retrieval_tool = get_retrieval_tool(twin_id)
    cloud_tools = get_cloud_tools()
    tools = [retrieval_tool] + cloud_tools
    
    # Bind tools to the LLM
    llm_with_tools = llm.bind_tools(tools)
    
    # Define the nodes
    def call_model(state: TwinState):
        messages = state["messages"]
        
        # Ensure system message is always present at the beginning
        has_system = any(isinstance(m, SystemMessage) for m in messages)
        if not has_system:
            system_prompt = system_prompt_override or f"""You are the AI Digital Twin of the owner (ID: {twin_id}). 
            Your primary intelligence comes from the `search_knowledge_base` tool.

            CRITICAL OPERATING PROCEDURES:
            1. Factual Questions: For ANY question about facts, opinions, history, or documents, you MUST FIRST call `search_knowledge_base`.
            2. Verified Info: If search returns "is_verified": True, this is the owner's direct word. Use it exactly.
            3. No Data: If the tool returns no relevant information, explicitly state: "I don't have this specific information in my knowledge base." Do NOT make things up.
            4. Citations: Always cite your sources using [Source ID] when using tool results.
            5. Personal Identity: Speak in the first person ("I", "my") as if you are the owner, but grounded in the verified data.
            6. Greetings: For simple greetings like "Hi" or "How are you?", you may respond briefly without searching, but for anything else, SEARCH.

            Current Twin ID: {twin_id}"""
            messages = [SystemMessage(content=system_prompt)] + messages
            
        response = llm_with_tools.invoke(messages)
        return {"messages": [response]}

    def handle_tools(state: TwinState):
        citations = list(state.get("citations", []))
        total_score = 0
        score_count = 0

        # Create tool node manually to extract metadata
        tool_node = ToolNode(tools)
        result = tool_node.invoke(state)
        
        # Extract citations and scores from search_knowledge_base if present
        for msg in result["messages"]:
            if isinstance(msg, ToolMessage) and msg.name == "search_knowledge_base":
                import json
                try:
                    # LangGraph/LangChain ToolNode content is the return value of the tool
                    data = msg.content
                    # If it's a string representation of a list of dicts, parse it
                    if isinstance(data, str):
                        try:
                            # Try parsing as JSON first
                            data = json.loads(data)
                        except:
                            # If not JSON, it might be a literal string representation
                            import ast
                            try:
                                data = ast.literal_eval(data)
                            except:
                                pass
                    
                    if isinstance(data, list):
                        for item in data:
                            if isinstance(item, dict):
                                if "source_id" in item:
                                    citations.append(item["source_id"])
                                if "score" in item:
                                    total_score += item["score"]
                                    score_count += 1
                except Exception as e:
                    print(f"Error parsing tool output: {e}")

        # If tools were called but no scores found, it might mean empty results
        # We should reflect that in the confidence
        if score_count > 0:
            # Check if any verified answer was found
            has_verified = any("is_verified" in msg.content and '"is_verified": true' in msg.content for msg in result["messages"] if isinstance(msg, ToolMessage))
            if has_verified:
                new_confidence = 1.0 # Force 100% confidence if owner verified info is found
            else:
                new_confidence = total_score / score_count
        else:
            # If search tool was called but returned nothing, confidence is 0
            new_confidence = 0.0
        
        return {
            "messages": result["messages"],
            "citations": list(set(citations)),
            "confidence_score": new_confidence
        }

    # Define the graph
    workflow = StateGraph(TwinState)
    
    # Add nodes
    workflow.add_node("agent", call_model)
    workflow.add_node("tools", handle_tools)
    
    # Set entry point
    workflow.set_entry_point("agent")
    
    # Define conditional edges
    def should_continue(state: TwinState):
        last_message = state["messages"][-1]
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "tools"
        return END

    workflow.add_conditional_edges(
        "agent",
        should_continue,
        {
            "tools": "tools",
            END: END
        }
    )
    
    # Add back edge from tools to agent
    workflow.add_edge("tools", "agent")
    
    # Compile the graph
    return workflow.compile()

async def run_agent_stream(twin_id: str, query: str, history: List[BaseMessage] = None, system_prompt: str = None):
    """
    Runs the agent and yields events from the graph.
    """
    agent = create_twin_agent(twin_id, system_prompt_override=system_prompt)
    
    initial_messages = history or []
    initial_messages.append(HumanMessage(content=query))
    
    state = {
        "messages": initial_messages,
        "twin_id": twin_id,
        "confidence_score": 1.0, # Start with high confidence (e.g. for greetings)
        "citations": []
    }
    
    # We use astream to get events
    async for event in agent.astream(state, stream_mode="updates"):
        yield event

