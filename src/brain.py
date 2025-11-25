from typing import Annotated, TypedDict, List
from langgraph.graph import StateGraph
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.sqlite import SqliteSaver
from langchain_core.messages import BaseMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from src.tools import get_core_tools
from src.memory import recall_memory, save_to_memory

class CoreState(TypedDict):
    messages: Annotated[List[BaseMessage], "add_messages"]
    context: str
    
def get_core_brain():
    tools = get_core_tools()
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0,
        max_queries=2
    )
    llm_with_tools = llm.bind_tools(tools)
    
    def recall_node(state: CoreState):
        last_message = state["messages"][-1].content
        
        memories = recall_memory(last_message)
        context_str = "\n".join(memories)
        return {"context": context_str}
    
    def agent_node(state: CoreState):
        context = state.get("context", "")
        system_msg = SystemMessage(
            content=f"""You are CORE. An advanced autonomous AI.
            
            RELEVANT LONG-TERM MEMORIES:
            {context}
            
            TOOLS AVAILABLE:
            - Browser: Navigate websites, click buttons.
            - Shell: Run terminal commands.
            - Filesystem: Read/Write files.
            
            INSTRUCTIONS:
            1. If you learn a new fact about the user, SAVE it using the available tools (or just keep it in context).
            2. When browsing, wait for pages to load.
            3. Be careful with Shell commands.
            """
        )
        
        message = [system_msg] + state["messages"]
        response = llm_with_tools.invoke(message)
        return {"messages": [response]}
    
    workflow = StateGraph(CoreState)
    workflow.add_node("recall", recall_node)
    workflow.add_node("agent", agent_node)
    workflow.add_node("tools", ToolNode(tools))
    
    workflow.set_entry_point("recall")
    workflow.add_edge("recall", "agent")
    workflow.add_conditional_edges("agent", tools_condition)
    workflow.add_edge("tools", "agent")
    memory = SqliteSaver.from_conn_string("core_state.db")
    
    return workflow.compile(checkpointer=memory)
    