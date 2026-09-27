"""
tools.py - Implementation of system tools/functions callable by the AI Assistant.
Includes: Web Search, Application Control, Utility Info (Time/Date/Weather), and Media Playback.
"""

import datetime
import os
import subprocess
import urllib.parse
import webbrowser
import requests
import config

# Try importing pywhatkit for YouTube automation, provide fallback if missing
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
    
    Args:
        query (str): Search term or URL.
    Returns:
        str: Status message for the assistant to report back.
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
    
    Args:
        app_name (str): Name or executable of the application to open.
    Returns:
        str: Status message indicating success or failure.
    """
    key = app_name.lower().strip()
    executable = config.APP_MAP.get(key, key)
    
    try:
        if os.name == 'nt':  # Windows
            # Use start command to execute application asynchronously
            subprocess.Popen(f"start {executable}", shell=True)
        elif os.name == 'posix':  # macOS / Linux
            subprocess.Popen([executable])
        else:
            return f"Unsupported Operating System: {os.name}"
            
        return f"Successfully launched application: '{app_name}'."
    except Exception as e:
        return f"Failed to open '{app_name}'. Error details: {str(e)}"


def get_utility_info(info_type: str, location: str = "") -> str:
    """
    Retrieves utility information such as current system time, date, or local weather.
    
    Args:
        info_type (str): Type of utility requested ('time', 'date', 'weather').
        location (str, optional): City or location name for weather lookup.
    Returns:
        str: Natural language summary of requested information.
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
            # Fetch weather from lightweight wttr.in weather API service
            url = f"https://wttr.in/{urllib.parse.quote(target_location)}?format=3"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                weather_text = response.text.strip()
                return f"Weather update: {weather_text}"
            else:
                return "Unable to fetch weather information right now."
        except Exception as e:
            return f"Weather lookup failed due to network error: {str(e)}"

    else:
        return f"Unknown utility type requested: '{info_type}'."


def play_media(query: str) -> str:
    """
    Searches YouTube and plays the requested video or audio track.
    
    Args:
        query (str): Song title, artist, or video search term.
    Returns:
        str: Status message.
    """
    clean_query = query.strip()
    if HAS_PYWHATKIT:
        try:
            pywhatkit.playonyt(clean_query)
            return f"Playing '{clean_query}' on YouTube."
        except Exception:
            pass  # Fall back to direct browser link

    # Fallback: direct YouTube search in browser
    encoded = urllib.parse.quote_plus(clean_query)
    yt_url = f"https://www.youtube.com/results?search_query={encoded}"
    webbrowser.open(yt_url)
    return f"Opened YouTube search results for '{clean_query}'."


# ==========================================
# FUNCTION CALLING SCHEMAS FOR LLM INTEGRATION
# ==========================================

TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Searches Google or opens web pages in the user's browser.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query or web address to search for."
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "open_application",
            "description": "Opens a local desktop application like Notepad, Calculator, Chrome, Command Prompt, Paint, etc.",
            "parameters": {
                "type": "object",
                "properties": {
                    "app_name": {
                        "type": "string",
                        "description": "The name of the application to launch (e.g., 'notepad', 'calculator', 'chrome', 'cmd')."
                    }
                },
                "required": ["app_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_utility_info",
            "description": "Gets system time, date, day of week, or current weather for a location.",
            "parameters": {
                "type": "object",
                "properties": {
                    "info_type": {
                        "type": "string",
                        "enum": ["time", "date", "weather"],
                        "description": "The type of utility information requested ('time', 'date', or 'weather')."
                    },
                    "location": {
                        "type": "string",
                        "description": "The city or location name if requesting weather (optional)."
                    }
                },
                "required": ["info_type"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "play_media",
            "description": "Searches and plays a song, music video, or video on YouTube.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The title of the song, artist, or video to play."
                    }
                },
                "required": ["query"]
            }
        }
    }
]

# Dispatcher mapping function names to Python functions
TOOL_DISPATCHER = {
    "web_search": web_search,
    "open_application": open_application,
    "get_utility_info": get_utility_info,
    "play_media": play_media
}


def execute_tool_call(tool_name: str, arguments: dict) -> str:
    """
    Executes a requested tool function with provided keyword arguments.
    
    Args:
        tool_name (str): Function name as defined in schema.
        arguments (dict): Parsed JSON arguments dict.
    Returns:
        str: Output result of tool execution.
    """
    func = TOOL_DISPATCHER.get(tool_name)
    if not func:
        return f"Error: Tool '{tool_name}' not found."
    try:
        return func(**arguments)
    except Exception as e:
        return f"Error executing tool '{tool_name}': {str(e)}"
