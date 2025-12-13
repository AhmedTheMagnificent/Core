from langchain_community.agent_toolkits import PlayWrightBrowserToolkit
from langchain_community.agent_toolkits import FileManagementToolkit

from src.windows_tools import (
    WindowsShellTool, 
    WindowTool, 
    OpenAppTool, 
    GlobalTypeTool, 
    DesktopShotTool
)

def get_tools(async_browser):
    file_management_tools = FileManagementToolkit()
    playwright_browser_tools = PlayWrightBrowserToolkit(async_browser=async_browser)
    windows_tools = [
        WindowsShellTool(),
        WindowTool(),
        OpenAppTool(),
        GlobalTypeTool(),
        DesktopShotTool()
    ]
    
    return (
        file_management_tools.get_tools() +
        playwright_browser_tools.get_tools() +
        windows_tools
    )


