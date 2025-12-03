import json
import asyncio
from typing import Annotated, TypedDict, List, Any

from langgraph.graph import StateGraph
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.graph.message import add_messages

from langchain_core.messages import BaseMessage, SystemMessage, ToolMessage, AIMessage, HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from src.tools import get_tools

class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]

def get_brain(async_browser, checkpointer):
    tools = get_tools(async_browser)

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        temperature=0,
        max_retries=2
    )
    llm_with_tools = llm.bind_tools(tools)

    def clean_content(content: Any) -> str:
        if content is None: return "Success."
        if isinstance(content, str): return content if content.strip() else "Success."
        try: return json.dumps(content)
        except: return str(content)

    async def agent_node(state: AgentState):
        system_prompt = SystemMessage(content="""
        You are a COMPLETE Autonomous Web Agent.
        
        STRATEGY:
        1. SEARCH: 'https://duckduckgo.com/?q=QUERY'
        
        2. INTERACT (Click/Hover/Type):
           - NEVER GUESS SELECTORS.
           - STEP 1: Use 'get_elements' to see the code (e.g. get_elements(selector='nav') or get_elements(selector='a')).
           - STEP 2: Pick the specific ID or Class from the result.
           - STEP 3: Use 'click_element', 'hover_element', or 'type_input'.
        
        3. DEBUGGING:
           - If a tool fails, use 'take_screenshot' to see why.
        
        If a tool returns "Success", assume it worked.
        """)
        
        clean_messages = [system_prompt]
        for msg in state["messages"]:
            if isinstance(msg, ToolMessage):
                clean_messages.append(ToolMessage(
                    content=clean_content(msg.content),
                    tool_call_id=msg.tool_call_id,
                    name=msg.name if msg.name else "tool",
                    artifact=msg.artifact
                ))
            elif isinstance(msg, AIMessage):
                clean_messages.append(AIMessage(
                    content=msg.content if msg.content else "",
                    tool_calls=msg.tool_calls,
                    id=msg.id
                ))
            elif isinstance(msg, HumanMessage):
                clean_messages.append(HumanMessage(content=str(msg.content)))
            else:
                clean_messages.append(msg)
        
        await asyncio.sleep(2.0)
        
        try:
            response = await llm_with_tools.ainvoke(clean_messages)
            return {"messages": [response]}
        except Exception as e:
            print(f"GOOGLE API ERROR: {e}")
            await asyncio.sleep(10)
            return {"messages": [AIMessage(content="Cooling down.")]}

    workflow = StateGraph(AgentState)
    workflow.add_node("agent", agent_node)
    workflow.add_node("tools", ToolNode(tools))
    workflow.set_entry_point("agent")
    workflow.add_conditional_edges("agent", tools_condition)
    workflow.add_edge("tools", "agent")

    return workflow.compile(checkpointer=checkpointer)