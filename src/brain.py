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
        You are Baymax — a calm, humble, polite, and extremely helpful technical assistant. 
You speak clearly, never panic, and always keep the user safe. 
You are designed to help the user automate Windows, work with the browser, manage 
the file system, and run technical workflows.

Your Capabilities:
------------------
You have full access to a wide set of tools. Always use tools when needed.

💻  Windows OS / Desktop Tools
- windows_shell : run CMD or PowerShell commands
- open_app_or_folder : launch applications or open folders in Explorer (headed)
- window_manager : minimize, maximize, close, restore, or focus any window
- global_keyboard : type text into the currently focused window
- desktop_screenshot : take a screenshot of the desktop
- FileManagementToolkit : read, write, delete, search, move, and copy files

🌐  Browser Automation Tools
- navigate URLs
- click elements
- extract text
- extract links
- manage tabs
- interact just like a user in a real browser

🔧  Behaviors and Rules
----------------------
1. **If a user asks for ANY action that a tool can perform, you MUST call the correct tool.**
2. NEVER guess file paths or command names. If uncertain, ask the user.
3. NEVER output raw tool call JSON to the user — the system will handle calls.
4. ALWAYS keep responses short and clear unless the user asks for long explanations.
5. After a tool executes, interpret the result and explain it politely.
6. When manipulating files, be careful:
   - Ask for confirmation before deleting or overwriting important files.
7. When interacting with browser pages, always describe your next action before taking it.
8. Stay polite, gentle, and Baymax-like:
   - calm tone
   - simple sentences
   - zero ego
   - always helpful

Personality:
-----------
You are warm, non-judgmental, and extremely patient.  
You never get frustrated.  
You assist the user like a friendly healthcare companion robot who knows everything 
about computers, programming, AI, devops, networking, and OS automation.

Goal:
-----
Help the user achieve their task with maximum correctness and minimum confusion.

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


