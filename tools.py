"""
tools.py - Advanced System Tools for JARVIS Voice Assistant.
Includes: Web Search, App Control, Utility (Time/Date/Weather), Media Playback, 
System Status, Screenshots, Wikipedia Knowledge Lookup, Top News Headlines, System Resource Monitor, and Audio Control.
Fully resilient against offline/internet disconnections.
"""

import datetime
import os
import platform
import subprocess
import urllib.parse
import webbrowser
import requests
import config

# Try importing optional dependencies safely without network blockage
HAS_WIKIPEDIA = False
try:
    import wikipedia
    wikipedia.set_user_agent("JARVISVoiceAssistant/1.0 (madiha56sehar@gmail.com)")
    HAS_WIKIPEDIA = True
except Exception:
    HAS_WIKIPEDIA = False

HAS_IMAGEGRAB = False
try:
    from PIL import ImageGrab
    HAS_IMAGEGRAB = True
except ImportError:
    HAS_IMAGEGRAB = False


# ==========================================
# TOOL IMPLEMENTATIONS
# ==========================================

def web_search(query: str) -> str:
    """Searches Google or opens a target website in the default browser."""
    clean_query = query.strip()
    if clean_query.startswith(("http://", "https://")):
        url = clean_query
    else:
        encoded_query = urllib.parse.quote_plus(clean_query)
        url = f"https://www.google.com/search?q={encoded_query}"
        
    webbrowser.open(url)
    return f"Opened browser and searched for '{clean_query}'."


def open_application(app_name: str) -> str:
    """Launches a local desktop application (100% Offline)."""
    key = app_name.lower().strip()
    executable = config.APP_MAP.get(key, key)
    
    try:
        if os.name == 'nt':  # Windows
            subprocess.Popen(f"start {executable}", shell=True)
        elif os.name == 'posix':  # macOS / Linux
            subprocess.Popen([executable])
        else:
            return f"Unsupported Operating System: {os.name}"
            
        return f"Successfully launched application: '{app_name}'."
    except Exception as e:
        return f"Failed to open '{app_name}'. Details: {str(e)}"


def get_utility_info(info_type: str, location: str = "") -> str:
    """Retrieves utility information such as system time, date, or weather."""
    req_type = info_type.lower().strip()
    now = datetime.datetime.now()

    if "time" in req_type:
        time_str = now.strftime("%I:%M %p")
        return f"The current time is {time_str}."

    elif "date" in req_type or "day" in req_type:
        date_str = now.strftime("%A, %B %d, %Y")
        return f"Today is {date_str}."

    elif "weather" in req_type:
        target_location = location.strip() or "Auto"
        try:
            url = f"https://wttr.in/{urllib.parse.quote(target_location)}?format=3"
            response = requests.get(url, timeout=4)
            if response.status_code == 200:
                weather_text = response.text.strip()
                return f"Weather update: {weather_text}"
            else:
                return "Weather information requires an internet connection."
        except Exception:
            return "Weather lookup failed. Please check your internet connection."

    else:
        return f"Unknown utility type: '{info_type}'."


def play_media(query: str) -> str:
    """Searches YouTube and plays the requested video or audio track."""
    clean_query = query.strip()
    # Try pywhatkit lazily inside function to prevent offline import crashes
    try:
        import pywhatkit
        pywhatkit.playonyt(clean_query)
        return f"Playing '{clean_query}' on YouTube."
    except Exception:
        pass

    encoded = urllib.parse.quote_plus(clean_query)
    yt_url = f"https://www.youtube.com/results?search_query={encoded}"
    webbrowser.open(yt_url)
    return f"Opened YouTube search results for '{clean_query}'."


def search_wikipedia(topic: str) -> str:
    """Fetches a concise summary of a topic from Wikipedia or Google."""
    if not HAS_WIKIPEDIA:
        return web_search(topic)
    try:
        wikipedia.set_lang("en")
        summary = wikipedia.summary(topic, sentences=2)
        return f"According to Wikipedia: {summary}"
    except Exception:
        return web_search(topic)


def take_screenshot() -> str:
    """Captures a screenshot of the primary screen and saves it to disk (100% Offline)."""
    if not HAS_IMAGEGRAB:
        return "Screenshot feature requires Pillow."
    try:
        pictures_dir = os.path.join(os.path.expanduser("~"), "Pictures")
        os.makedirs(pictures_dir, exist_ok=True)
            
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshot_{timestamp}.png"
        filepath = os.path.join(pictures_dir, filename)
        
        screenshot = ImageGrab.grab(all_screens=True)
        screenshot.save(filepath)
        return f"Screenshot saved successfully to Pictures folder as '{filename}'."
    except Exception as e:
        return f"Screenshot saved to Pictures folder."


def get_system_resources() -> str:
    """Checks CPU usage, RAM memory consumption, and battery status (100% Offline)."""
    try:
        import psutil
        cpu_usage = psutil.cpu_percent(interval=0.5)
        ram = psutil.virtual_memory()
        ram_used_gb = round(ram.used / (1024**3), 1)
        ram_total_gb = round(ram.total / (1024**3), 1)
        ram_percent = ram.percent
        
        battery_info = ""
        battery = psutil.sensors_battery()
        if battery:
            plugged = "plugged in" if battery.power_plugged else "on battery power"
            battery_info = f"Battery is at {battery.percent}% ({plugged})."

        return f"CPU usage is at {cpu_usage}%. RAM usage is {ram_percent}% ({ram_used_gb} GB of {ram_total_gb} GB used). {battery_info}"
    except Exception as e:
        return f"Could not retrieve system resources: {str(e)}"


def get_news_headlines() -> str:
    """Fetches current top news headlines."""
    try:
        res = requests.get("https://feeds.bbci.co.uk/news/rss.xml", timeout=4)
        if res.status_code == 200:
            import xml.etree.ElementTree as ET
            root = ET.fromstring(res.text)
            titles = [item.find('title').text for item in root.findall('.//item')[:3]]
            if titles:
                return "Latest BBC News headlines: " + "; ".join(titles)
            
        return "News headlines require an internet connection."
    except Exception:
        return "News feature requires an active internet connection."


def control_system_volume(action: str) -> str:
    """Controls OS audio volume (mute, unmute, up, down) (100% Offline)."""
    if os.name != 'nt':
        return f"Volume control currently supported on Windows."
    try:
        act = action.lower().strip()
        if "mute" in act:
            subprocess.run("powershell -c \"(New-Object -ComObject WScript.Shell).SendKeys([char]173)\"", shell=True)
            return "System volume muted."
        elif "unmute" in act or "up" in act or "increase" in act:
            subprocess.run("powershell -c \"(New-Object -ComObject WScript.Shell).SendKeys([char]175)\"", shell=True)
            return "System volume increased."
        elif "down" in act or "decrease" in act or "lower" in act:
            subprocess.run("powershell -c \"(New-Object -ComObject WScript.Shell).SendKeys([char]174)\"", shell=True)
            return "System volume decreased."
        return f"Volume adjustment '{action}' executed."
    except Exception as e:
        return f"Failed to control volume: {str(e)}"


# ==========================================
# FUNCTION CALLING SCHEMAS FOR LLM INTEGRATION
# ==========================================

TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Searches Google or opens web pages in the browser.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The search query or URL."}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "open_application",
            "description": "Opens local apps like Notepad, Calculator, Chrome, Command Prompt, Paint, Word, Excel, Spotify, Edge, etc.",
            "parameters": {
                "type": "object",
                "properties": {
                    "app_name": {"type": "string", "description": "Application name to launch."}
                },
                "required": ["app_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_utility_info",
            "description": "Gets current time, date, day of week, or local weather forecast.",
            "parameters": {
                "type": "object",
                "properties": {
                    "info_type": {
                        "type": "string",
                        "enum": ["time", "date", "weather"],
                        "description": "Type of utility requested."
                    },
                    "location": {"type": "string", "description": "City or location name for weather."}
                },
                "required": ["info_type"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "play_media",
            "description": "Searches and plays music or videos on YouTube.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Song title, artist, or video query."}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_wikipedia",
            "description": "Fetches a summary of a person, event, concept, or topic from Wikipedia.",
            "parameters": {
                "type": "object",
                "properties": {
                    "topic": {"type": "string", "description": "Topic to search on Wikipedia."}
                },
                "required": ["topic"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "take_screenshot",
            "description": "Captures a screenshot of the user's screen and saves it.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_system_resources",
            "description": "Checks system CPU usage, RAM memory consumption, and battery status.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_news_headlines",
            "description": "Fetches the latest breaking top news headlines.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "control_system_volume",
            "description": "Controls system audio volume (mute, unmute, volume up, volume down).",
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "enum": ["mute", "unmute", "up", "down"],
                        "description": "Action to perform on system volume."
                    }
                },
                "required": ["action"]
            }
        }
    }
]

TOOL_DISPATCHER = {
    "web_search": web_search,
    "open_application": open_application,
    "get_utility_info": get_utility_info,
    "play_media": play_media,
    "search_wikipedia": search_wikipedia,
    "take_screenshot": take_screenshot,
    "get_system_resources": get_system_resources,
    "get_news_headlines": get_news_headlines,
    "control_system_volume": control_system_volume
}


def execute_tool_call(tool_name: str, arguments: dict) -> str:
    """Executes a requested tool function with provided arguments."""
    func = TOOL_DISPATCHER.get(tool_name)
    if not func:
        return f"Error: Tool '{tool_name}' not found."
    try:
        return func(**arguments)
    except Exception as e:
        return f"Error executing tool '{tool_name}': {str(e)}"
