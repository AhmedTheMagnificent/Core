import uuid
import sys
import asyncio
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from playwright.async_api import async_playwright
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

from src.brain import get_brain

load_dotenv()

async def run_chat():
    print("ONLINE")
    
    async with AsyncSqliteSaver.from_conn_string("browser_state.db") as memory:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            
            try:
                graph = get_brain(browser, memory)
            except Exception as e:
                print(f"Startup Error: {e}")
                return

            session_id = str(uuid.uuid4())
            config = {"configurable": {"thread_id": session_id}}
            print(f"Session ID: {session_id}")

            while True:
                try:
                    user_input = await asyncio.to_thread(input, "\nCommand > ")
                    if user_input.lower() in ["exit", "quit"]: break

                    print("... Working ...")

                    async for event in graph.astream(
                        {"messages": [HumanMessage(content=user_input)]},
                        config,
                        stream_mode="values"
                    ):
                        if "messages" in event:
                            msg = event["messages"][-1]
                            
                            if msg.type == "ai" and msg.tool_calls:
                                for tool in msg.tool_calls:
                                    args = tool['args']
                                    print(f"   [Tool] {tool['name']} -> {str(args)[:100]}...")
                            
                            elif msg.type == "ai" and msg.content and not msg.tool_calls:
                                print(f"\nAGENT: {msg.content}")

                except KeyboardInterrupt: break
                except Exception as e: print(f"Runtime Error: {e}")

            await browser.close()

if __name__ == "__main__":
    if sys.platform.startswith("win"):
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    asyncio.run(run_chat())