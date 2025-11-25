import os
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_community.agent_toolkits.file_management.toolkit import FileManagementToolkit
from langchain_community.agent_toolkits.playwright.toolkit import PlaywrightBrowserToolkit
from langchain_community.tools.playwright.utils import create_sync_playwright_browser
from langchain_community.tools.shell.tool import ShellTool


browser = create_sync_playwright_browser(headless=False)

def get_core_tools():
    tools = []
    
    search_tool = TavilySearchResults(max_results=3)
    tools.append(search_tool)
    
    file_toolkit = FileManagementToolkit(
        root_dir=os.getcwd(),
        selected_tools=["read_file", "write_file", "list_directory"]
    )
    tools.extend(file_toolkit.get_tools())
    
    browser_toolkit = PlaywrightBrowserToolkit.from_browser_tools(
        browser,
        selected_tools=["click_element", "navigate_browser", "extract_text", "get_elements"]
    )
    tools.extend(browser_toolkit.get_tools())
    
    shell_tool = ShellTool()
    shell_tool.description = shell_tool.description + f"args {shell_tool.args}".replace(
        "{", "{{"
    ).replace("}", "}}")
    tools.append(shell_tool)
    
    return tools