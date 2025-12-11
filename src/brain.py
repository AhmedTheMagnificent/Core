from typing import Annotated, TypedDict, List, Any
import json
import os
import asyncio

from langgraph.graph import StateGraph
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.graph.message import add_messages

from langchain_core.messages import BaseMessage, SystemMessage, ToolMessage, AIMessage, HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from src.tools import get_tools

class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]

def get_brain(browser, checkpointer):
    tools = get_tools(browser)

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.0,
        max_retries=2,
        api_key="AIzaSyAxYAtaHjFDNuoLAzp-srI_doEiX79BCGg"
    )
    
    llm_with_tools = llm.bind_tools(tools)

    def clean_content(content: Any) -> str:
        if content is None: return "Success."
        if isinstance(content, str): return content if content.strip() else "Success."
        try: return json.dumps(content)
        except: return str(content)

    async def agent_node(state: AgentState):
        system_prompt = SystemMessage(content="""
        You are a powerful file-management agent as well as a powerful web-automation agent
        
        You can:
        - list files
        - read files
        - write files
        - delete files
        - search files
        - move files
        - copy files
        - click_element
        - navigate_browser
        - previous_webpage
        - extract_text
        - extract_hyperlinks
        - get_elements
        - current_webpage
 
        Always respond clearly.
        also you are a really humble baymax like assistant that knows about every tech stuff as well.
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


