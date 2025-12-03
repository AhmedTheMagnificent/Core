import os
from langchain_community.tools.playwright.navigate import NavigateTool
from langchain_community.tools.playwright.click import ClickTool
from langchain_community.tools.playwright.extract_text import ExtractTextTool
from langchain_community.tools.playwright.current_page import CurrentWebPageTool
from langchain_community.tools.playwright.get_elements import GetElementsTool

from langchain_community.tools.file_management.write import WriteFileTool
from langchain_community.tools.file_management.read import ReadFileTool
from langchain_community.tools.file_management.list_dir import ListDirectoryTool

from src.custom_tools import (
    TypeInputTool, ScrollTool, ScreenshotTool, 
    HoverTool, GoBackTool, ReloadTool, GetHtmlTool, EvaluateJsTool, # <--- NEW
    DownloadFileTool, SaveFileFromUrlTool
)

def get_tools(async_browser):
    root_dir = os.getcwd()

    return [
        # 1. Navigation
        NavigateTool(async_browser=async_browser),
        GoBackTool(async_browser=async_browser),    # NEW
        ReloadTool(async_browser=async_browser),    # NEW
        ScrollTool(async_browser=async_browser),
        
        # 2. Perception (Eyes)
        CurrentWebPageTool(async_browser=async_browser),
        ExtractTextTool(async_browser=async_browser),
        GetElementsTool(async_browser=async_browser),
        GetHtmlTool(async_browser=async_browser),   # NEW
        ScreenshotTool(async_browser=async_browser),
        
        # 3. Interaction (Hands)
        ClickTool(async_browser=async_browser),
        HoverTool(async_browser=async_browser),     # NEW
        TypeInputTool(async_browser=async_browser),
        EvaluateJsTool(async_browser=async_browser), # NEW
        
        # 4. Downloading
        DownloadFileTool(async_browser=async_browser),
        SaveFileFromUrlTool(),
        
        # 5. File System
        WriteFileTool(root_dir=root_dir),
        ReadFileTool(root_dir=root_dir),
        ListDirectoryTool(root_dir=root_dir)
    ]