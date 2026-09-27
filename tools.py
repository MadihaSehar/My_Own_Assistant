"""
tools.py - Implementation of system tools/functions callable by the AI Assistant.
Includes: Web Search, Application Control, Utility Info, Media Playback, and System Status.
"""

import datetime
import os
import platform
import subprocess
import urllib.parse
import webbrowser
import requests
import config

try:
    import pywhatkit
    HAS_PYWHATKIT = True
except ImportError:
    HAS_PYWHATKIT = False


# ==========================================
# TOOL IMPLEMENTATIONS
# ==========================================

def web_search(query: str) -> str:
    """
    Searches Google or opens a target website in the default browser.
    """
    clean_query = query.strip()
    if clean_query.startswith(("http://", "https://")):
        url = clean_query
    else:
        encoded_query = urllib.parse.quote_plus(clean_query)
        url = f"https://www.google.com/search?q={encoded_query}"
        
    webbrowser.open(url)
    return f"Opened browser and searched for '{clean_query}'."


def open_application(app_name: str) -> str:
    """
    Launches a local application on the host operating system.
    """
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
    """
    Retrieves utility information such as current system time, date, or local weather.
    """
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
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                weather_text = response.text.strip()
                return f"Weather update: {weather_text}"
            else:
                return "Unable to fetch weather information right now."
        except Exception as e:
            return f"Weather lookup failed: {str(e)}"

    else:
        return f"Unknown utility type: '{info_type}'."


def play_media(query: str) -> str:
    """
    Searches YouTube and plays the requested video or audio track.
    """
    clean_query = query.strip()
    if HAS_PYWHATKIT:
        try:
            pywhatkit.playonyt(clean_query)
            return f"Playing '{clean_query}' on YouTube."
        except Exception:
            pass

    encoded = urllib.parse.quote_plus(clean_query)
    yt_url = f"https://www.youtube.com/results?search_query={encoded}"
    webbrowser.open(yt_url)
    return f"Opened YouTube search results for '{clean_query}'."


def get_system_status() -> str:
    """
    Checks system OS, platform details, and battery status.
    """
    os_info = f"{platform.system()} {platform.release()}"
    battery_str = "Battery status not available"
    try:
        import psutil
        battery = psutil.sensors_battery()
        if battery:
            plugged = "plugged in" if battery.power_plugged else "on battery power"
            battery_str = f"Battery is at {battery.percent}% ({plugged})"
    except Exception:
        pass

    return f"System running on {os_info}. {battery_str}."


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
            "description": "Opens local apps like Notepad, Calculator, Chrome, Command Prompt, Paint, Word, Excel, etc.",
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
            "name": "get_system_status",
            "description": "Checks system operating system, battery percentage, and hardware status.",
            "parameters": {"type": "object", "properties": {}}
        }
    }
]

TOOL_DISPATCHER = {
    "web_search": web_search,
    "open_application": open_application,
    "get_utility_info": get_utility_info,
    "play_media": play_media,
    "get_system_status": get_system_status
}


def execute_tool_call(tool_name: str, arguments: dict) -> str:
    """
    Executes a requested tool function with provided arguments.
    """
    func = TOOL_DISPATCHER.get(tool_name)
    if not func:
        return f"Error: Tool '{tool_name}' not found."
    try:
        return func(**arguments)
    except Exception as e:
        return f"Error executing tool '{tool_name}': {str(e)}"
