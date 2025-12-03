import os
import requests
import asyncio
from typing import Optional, Type, Any
from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool

# --- HELPER FUNCTION (Replaces the broken LangChain helper) ---
async def _get_page(browser):
    """
    Manually gets the current page from the Async Browser.
    """
    if not browser:
        raise ValueError("Browser is not initialized.")
    
    # 1. Get or Create Context
    if not browser.contexts:
        context = await browser.new_context()
    else:
        context = browser.contexts[0]

    # 2. Get or Create Page
    if not context.pages:
        page = await context.new_page()
    else:
        page = context.pages[0]
        
    return page

# --- TOOL 1: TYPE INPUT ---
class TypeInputArgs(BaseModel):
    selector: str = Field(description="CSS selector for the input box.")
    text: str = Field(description="The text to type.")
    submit: bool = Field(default=False, description="Press Enter after typing?")

class TypeInputTool(BaseTool):
    name: str = "type_input"
    description: str = "Type text into search bars or forms."
    args_schema: Type[BaseModel] = TypeInputArgs
    async_browser: Any = None
    def __init__(self, async_browser): super().__init__(); self.async_browser = async_browser
    def _run(self, selector: str, text: str, submit: bool = False): raise NotImplementedError
    
    async def _arun(self, selector: str, text: str, submit: bool = False):
        page = await _get_page(self.async_browser)
        try:
            await page.wait_for_selector(selector, state="visible", timeout=3000)
            await page.fill(selector, text)
            if submit: await page.press(selector, "Enter")
            return f"Success: Typed '{text}'"
        except Exception as e: return f"Error: {e}"

# --- TOOL 2: SCROLL ---
class ScrollArgs(BaseModel):
    direction: str = Field(description="'down' or 'up'")
    amount: int = Field(default=800)

class ScrollTool(BaseTool):
    name: str = "scroll_page"
    description: str = "Scroll the page."
    args_schema: Type[BaseModel] = ScrollArgs
    async_browser: Any = None
    def __init__(self, async_browser): super().__init__(); self.async_browser = async_browser
    def _run(self, direction: str, amount: int = 800): raise NotImplementedError
    
    async def _arun(self, direction: str, amount: int = 800):
        page = await _get_page(self.async_browser)
        script = f"window.scrollBy(0, {amount})" if direction == "down" else f"window.scrollBy(0, -{amount})"
        await page.evaluate(script)
        return f"Success: Scrolled {direction}"

# --- TOOL 3: JAVASCRIPT ---
class EvalJsArgs(BaseModel):
    script: str = Field(description="JavaScript code to execute.")

class EvaluateJsTool(BaseTool):
    name: str = "evaluate_javascript"
    description: str = "Execute custom JavaScript."
    args_schema: Type[BaseModel] = EvalJsArgs
    async_browser: Any = None
    def __init__(self, async_browser): super().__init__(); self.async_browser = async_browser
    def _run(self, script: str): raise NotImplementedError
    
    async def _arun(self, script: str):
        page = await _get_page(self.async_browser)
        # Listen for dialogs to prevent freezing
        page.on("dialog", lambda dialog: asyncio.create_task(dialog.accept()))
        # Sanitize script
        clean_script = script.strip().strip("`").replace("javascript", "").replace("js", "").strip()
        try:
            result = await page.evaluate(clean_script)
            return f"Success: JS Result: {str(result)}"
        except Exception as e:
            return f"Error executing JS: {e}"

# --- TOOL 4: SCREENSHOT ---
class ScreenshotTool(BaseTool):
    name: str = "take_screenshot"
    description: str = "Save image of page."
    async_browser: Any = None
    def __init__(self, async_browser): super().__init__(); self.async_browser = async_browser
    def _run(self): raise NotImplementedError
    
    async def _arun(self):
        page = await _get_page(self.async_browser)
        path = os.path.join(os.getcwd(), "screenshot.png")
        await page.screenshot(path=path)
        return f"Success: Saved to {path}"

# --- TOOL 5: HOVER ---
class HoverArgs(BaseModel): selector: str
class HoverTool(BaseTool):
    name: str = "hover_element"
    description: str = "Hover over an element."
    args_schema: Type[BaseModel] = HoverArgs
    async_browser: Any = None
    def __init__(self, async_browser): super().__init__(); self.async_browser = async_browser
    def _run(self, selector: str): raise NotImplementedError
    
    async def _arun(self, selector: str):
        page = await _get_page(self.async_browser)
        await page.hover(selector)
        return f"Success: Hovered {selector}"

# --- TOOL 6: NAVIGATION EXTRAS ---
class GoBackTool(BaseTool):
    name: str = "go_back"
    description: str = "Go back in history."
    async_browser: Any = None
    def __init__(self, async_browser): super().__init__(); self.async_browser = async_browser
    def _run(self): raise NotImplementedError
    async def _arun(self):
        page = await _get_page(self.async_browser)
        await page.go_back()
        return "Success: Went back."

class ReloadTool(BaseTool):
    name: str = "reload_page"
    description: str = "Reload page."
    async_browser: Any = None
    def __init__(self, async_browser): super().__init__(); self.async_browser = async_browser
    def _run(self): raise NotImplementedError
    async def _arun(self):
        page = await _get_page(self.async_browser)
        await page.reload()
        return "Success: Reloaded."

class GetHtmlTool(BaseTool):
    name: str = "get_html_source"
    description: str = "Get raw HTML."
    async_browser: Any = None
    def __init__(self, async_browser): super().__init__(); self.async_browser = async_browser
    def _run(self): raise NotImplementedError
    async def _arun(self):
        page = await _get_page(self.async_browser)
        content = await page.content()
        return content[:5000] # Truncate

# --- DOWNLOAD TOOLS ---
class DownloadInput(BaseModel):
    selector: str
    filename: Optional[str] = None
class DownloadFileTool(BaseTool):
    name: str = "download_file_via_click"
    description: str = "Click button to download."
    args_schema: Type[BaseModel] = DownloadInput
    async_browser: Any = None
    def __init__(self, async_browser): super().__init__(); self.async_browser = async_browser
    def _run(self, selector: str, filename: Optional[str] = None): raise NotImplementedError
    
    async def _arun(self, selector: str, filename: Optional[str] = None):
        page = await _get_page(self.async_browser)
        try:
            async with page.expect_download(timeout=10000) as download_info:
                await page.click(selector)
            download = await download_info.value
            final_name = filename if filename else download.suggested_filename
            save_path = os.path.join(os.getcwd(), final_name)
            await download.save_as(save_path)
            return f"Success: Saved to {save_path}"
        except Exception as e: return f"Error: {e}"

class SaveUrlInput(BaseModel):
    url: str
    filename: str
class SaveFileFromUrlTool(BaseTool):
    name: str = "save_file_from_url"
    description: str = "Download from Direct URL."
    args_schema: Type[BaseModel] = SaveUrlInput
    def _run(self, url: str, filename: str):
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            r = requests.get(url, headers=headers, stream=True)
            r.raise_for_status()
            save_path = os.path.join(os.getcwd(), filename)
            with open(save_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192): f.write(chunk)
            return f"Success: Saved to {save_path}"
        except Exception as e: return f"Error: {e}"
    async def _arun(self, url: str, filename: str): return self._run(url, filename)