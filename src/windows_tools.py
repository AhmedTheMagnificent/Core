import asyncio
import subprocess 
import os
import pyautogui
import pygetwindow as gw
from typing import Type, Any, Optional
from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool

pyautogui.FAILSAFE = True

class WindowsShellInput(BaseModel):
    command: str = Field(description="The Windows CMD or PowerShell command to execute.")
    use_powershell: bool = Field(default=False, description="Set True to use PowerShell, False for CMD.")

class WindowsShellTool(BaseTool):
    name: str = "windows_shell"
    description: str = "Execute system commands on Windows. Use this to check system info, manage files, open applications, or check network status."
    args_schema: Type[BaseModel] = WindowsShellInput
    
    def _run(self, command, use_powershell=False):
        raise NotImplementedError("Use async")
    
    async def _arun(self, command, use_powershell=False):
        if use_powershell:  shell_cmd = f"powershell.exe -Command \"{command}\""
        else:               shell_cmd = f"cmd.exe /c \"{command}\""
        print(f"   [OS] Executing: {shell_cmd}")
        
        try:
            process = await asyncio.create_subprocess_shell(
                shell_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            output = stdout.decode('utf-8', errors='ignore').strip()
            error = stderr.decode('utf-8', errors='ignore').strip()

            if process.returncode != 0:
                return f"Error (Exit Code {process.returncode}):\n{error}"
            
            return f"Output:\n{output}" if output else "Success: Command executed (No output)."

        except Exception as e:
            return f"System Error: {e}"
        
        
        
class WindowArgs(BaseModel):
    app_name: str = Field(description="Partial title of the window (e.g., 'Chrome', 'Notepad').")
    action: str = Field(description="Action: 'minimize', 'maximize', 'restore', 'close', 'focus'.")
    

class WindowTool(BaseTool):
    name: str = "window_manager"
    description: str = "Control desktop windows. Minimize, maximize, close, or bring apps to the front."
    args_schema: Type[BaseModel] = WindowArgs

    def _run(self, app_name: str, action: str): raise NotImplementedError
    
    def _arun(self, app_name: str, action: str):
        windows = gw.getWindowsWithTitle(app_name)
        if not windows: return f"Error: No open window found matching '{app_name}'."
        window = windows[0]
        try:
            if action == "minimize": window.minimize()
            elif action == "maximize": window.maximize()
            elif action == "restore": window.restore()
            elif action == "close": window.close()
            elif action == "focus": window.activate()
            else: return "Error: Unknown action."
            return f"Success: {action} performed on '{window.title}'."
        except Exception as e: return f"Error managing window: {e}"
        
    
class OpenArgs(BaseModel):
    path: str = Field(description="Path to folder (e.g., 'C:\\Users') or app name (e.g., 'notepad').")
    
    
class OpenAppTool(BaseTool):
    name: str = "open_app_or_folder"
    description: str = "Visually open a folder in Explorer or launch an application."
    args_schema: Type[BaseModel] = OpenArgs

    def _run(self, path: str): raise NotImplementedError
    
    async def _arun(self, path: str):
        try:
            os.startfile(path) 
            return f"Success: Opened '{path}' on the desktop."
        except Exception as e: return f"Error opening: {e}"
        
        
class GlobalTypeArgs(BaseModel):
    text: str = Field(description="Text to type.")

class GlobalTypeTool(BaseTool):
    name: str = "global_keyboard"
    description: str = "Type text into whatever window is currently focused on the desktop."
    args_schema: Type[BaseModel] = GlobalTypeArgs

    def _run(self, text: str): raise NotImplementedError
    async def _arun(self, text: str):
        try:
            pyautogui.write(text, interval=0.05)
            pyautogui.press('enter')
            return f"Success: Typed '{text}'."
        except Exception as e: return f"Error typing: {e}"
        

class DesktopShotTool(BaseTool):
    name: str = "desktop_screenshot"
    description: str = "Take a screenshot of the ENTIRE desktop screen."
    def _run(self): raise NotImplementedError
    async def _arun(self):
        try:
            screenshot = pyautogui.screenshot()
            path = os.path.join(os.getcwd(), "desktop_view.png")
            screenshot.save(path)
            return f"Success: Desktop screenshot saved to {path}"
        except Exception as e: return f"Error taking screenshot: {e}"