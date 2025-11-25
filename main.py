import sys
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.text import Text
from langchain_core.messages import HumanMessage, SystemMessage

# Import our Brain
from src.brain import build_core_brain

# 1. SETUP
load_dotenv()
console = Console()

def print_ai_response(text):
    """Helper to print a nice box for the answer."""
    console.print(Panel(
        Markdown(text),
        title="[bold green]CORE[/bold green]",
        border_style="green",
        expand=False
    ))

def print_tool_activity(tool_name, tool_input):
    """Helper to show what tool is being used."""
    console.print(f"[dim italic cyan]>> Action: Using {tool_name}[/dim italic cyan]")
    console.print(f"[dim italic]   Input: {tool_input}[/dim italic]")

def main():
    # Clear screen for a fresh start
    console.clear()
    console.print(Panel("[bold white]SYSTEM ONLINE: CORE V1.0[/bold white]", style="bold white on blue"))
    
    # 2. INITIALIZE BRAIN
    try:
        graph = get_core_brain()
    except Exception as e:
        console.print(f"[bold red]Startup Error: {e}[/bold red]")
        console.print("[yellow]Did you install the requirements? (pip install -r requirements.txt)[/yellow]")
        return

    # Configuration for Memory (Persistence)
    # Keeping thread_id constant means it remembers you across restarts
    config = {"configurable": {"thread_id": "main_user"}}

    # 3. MAIN LOOP
    while True:
        try:
            # Get User Input
            user_input = console.input("\n[bold yellow]User > [/bold yellow]")
            
            # Exit Commands
            if user_input.lower() in ["exit", "quit", "shutdown"]:
                console.print("[red]Shutting down Core...[/red]")
                break

            # 4. RUNNING THE GRAPH
            # We use a spinner so you know it's working
            with console.status("[bold cyan]Core is processing...[/bold cyan]", spinner="dots"):
                
                # Stream the events (Thinking -> Tool -> Thinking -> Answer)
                events = graph.stream(
                    {"messages": [HumanMessage(content=user_input)]},
                    config,
                    stream_mode="values"
                )

                for event in events:
                    if "messages" in event:
                        message = event["messages"][-1]
                        
                        # Case A: AI wants to use a Tool
                        if message.type == "ai" and message.tool_calls:
                            for tool in message.tool_calls:
                                print_tool_activity(tool["name"], tool["args"])
                        
                        # Case B: AI has a final answer (text content)
                        # We wait until it has content AND no tool calls to print the final block
                        elif message.type == "ai" and message.content and not message.tool_calls:
                            # We clear the spinner line just before printing result
                            pass 

            # Print the final message from the state (Last message)
            snapshot = graph.get_state(config)
            if snapshot.values and snapshot.values["messages"]:
                last_msg = snapshot.values["messages"][-1]
                if last_msg.type == "ai" and last_msg.content:
                    print_ai_response(last_msg.content)

        except KeyboardInterrupt:
            console.print("\n[red]Interrupted by user.[/red]")
            break
        except Exception as e:
            console.print(f"[bold red]Critical Error: {e}[/bold red]")

if __name__ == "__main__":
    main()