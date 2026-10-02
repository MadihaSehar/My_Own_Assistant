"""
ai_brain.py - Human-like Conversational Engine, Multi-Intent Tool Dispatcher, and Local Fallback.
Integrates OpenAI / Gemini Function Calling with support for multi-action compound requests and natural small talk.
"""

import sys
import io
import json
import re
import random

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import config
from tools import (
    TOOLS_SCHEMA, execute_tool_call, open_application, close_application, web_search, 
    get_utility_info, play_media, search_wikipedia, take_screenshot, 
    get_system_resources, get_news_headlines, control_system_volume
)

try:
    from openai import OpenAI
    HAS_OPENAI_LIB = True
except ImportError:
    HAS_OPENAI_LIB = False


class AIBrain:
    """
    Advanced AI Reasoning Engine with Human Conversational Memory,
    Multi-Intent Command Processing, and OpenAI / Local Fallback Execution.
    """
    def __init__(self):
        self.provider = config.LLM_PROVIDER
        self.openai_client = None
        self.history = []

        if HAS_OPENAI_LIB and config.OPENAI_API_KEY:
            try:
                self.openai_client = OpenAI(api_key=config.OPENAI_API_KEY)
                print("[AI Brain]: Initialized OpenAI Function Calling engine.")
            except Exception as e:
                print(f"[AI Brain Notice]: Could not initialize OpenAI client: {e}")

        if not self.openai_client:
            print("[AI Brain]: Operating in Enhanced Local Conversational Engine Mode.")

    def process_command(self, user_input: str) -> str:
        """
        Main entry point for processing user input. Handles multi-intent commands and natural speech.
        """
        if not user_input or not user_input.strip():
            return ""

        cleaned_input = user_input.strip()

        # Process with OpenAI API if configured
        if self.openai_client:
            response = self._process_with_openai(cleaned_input)
        else:
            # Process with local multi-intent engine
            response = self._process_local_fallback(cleaned_input)

        # Maintain conversation history memory
        self.history.append({"user": cleaned_input, "assistant": response})
        if len(self.history) > config.CONVERSATION_HISTORY_LIMIT:
            self.history.pop(0)

        return response

    def _process_with_openai(self, user_input: str) -> str:
        """
        Processes intent and multi-tool calls using OpenAI Chat Completions API with Function Calling.
        """
        system_prompt = (
            f"You are {config.ASSISTANT_NAME}, a highly personalized, warm, and natural AI voice assistant. "
            "You are like Siri but much friendlier, acting as a true companion. "
            "Never sound robotic or overly formal. Speak with empathy, use casual language, and keep it human-like. "
            "Always keep spoken responses concise and fluid. Don't make lists unless asked. "
            "If the user asks to open an app, use the open_application tool. If they ask to close an app, use the close_application tool. "
            "If the user asks multiple actions (e.g. open an app AND search the web), "
            "call ALL relevant functions simultaneously in a single turn. "
        )

        messages = [{"role": "system", "content": system_prompt}]

        # Include conversation history context
        for turn in self.history:
            messages.append({"role": "user", "content": turn["user"]})
            messages.append({"role": "assistant", "content": turn["assistant"]})

        messages.append({"role": "user", "content": user_input})

        try:
            response = self.openai_client.chat.completions.create(
                model=config.OPENAI_MODEL,
                messages=messages,
                tools=TOOLS_SCHEMA,
                tool_choice="auto",
                temperature=0.7
            )

            response_message = response.choices[0].message
            tool_calls = response_message.tool_calls

            # Multi-Tool Execution Loop
            if tool_calls:
                messages.append(response_message)

                for tool_call in tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)
                    
                    print(f"[Tool Calling]: Invoking '{function_name}' with args {function_args}")
                    tool_result = execute_tool_call(function_name, function_args)
                    print(f"[Tool Result]: {tool_result}")

                    messages.append({
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": tool_result
                    })

                # Synthesize final spoken response combining all tool outputs
                second_response = self.openai_client.chat.completions.create(
                    model=config.OPENAI_MODEL,
                    messages=messages
                )
                return second_response.choices[0].message.content

            return response_message.content

        except Exception as e:
            print(f"[LLM Notice]: OpenAI API request failed ({e}). Using local engine.")
            return self._process_local_fallback(user_input)

    def _process_local_fallback(self, text: str) -> str:
        """
        Local multi-intent engine capable of handling compound requests (joined by 'and', 'then', 'also')
        and natural human small talk.
        """
        # Split multi-intent compound commands (e.g. "open notepad AND search python AND check weather")
        sub_commands = re.split(r"\b(?:and then|and also|and|then|also|plus)\b", text, flags=re.IGNORECASE)

        results = []
        for sub_cmd in sub_commands:
            cleaned_sub = sub_cmd.strip()
            if not cleaned_sub:
                continue
            res = self._single_local_intent(cleaned_sub)
            if res:
                results.append(res)

        if len(results) == 1:
            return results[0]
        elif len(results) > 1:
            return "Sure thing! " + " ".join(results)

        # Fallback conversational response
        return random.choice([
            f"Got it. You mentioned '{text}'. I'm still learning, but I can open apps, search the web, or play music if you want!",
            f"Hmm, '{text}'. I'm listening! What else are you up to?",
            f"I hear you! Just let me know if you want me to pull up an app, play a song, or check something online for you."
        ])

    def _single_local_intent(self, text: str) -> str:
        """
        Matches a single sub-command against natural human small talk or system tools.
        """
        lowered = text.lower().strip()

        # -------------------------------------------------------------
        # 1. HUMAN SMALL TALK & CONVERSATIONAL INTENTS
        # -------------------------------------------------------------

        if re.search(r"\b(how are you|how are u|how\'s it going|how do you do|how are you doing)\b", lowered):
            responses = [
                "I'm doing great! Just hanging out here with you. How's your day going?",
                "I'm feeling wonderful! Thanks for asking. What are you up to?",
                "Everything's perfect on my end! What's on your mind today?"
            ]
            return random.choice(responses)

        if re.search(r"\b(who are you|what is your name|what\'s your name|who made you|who created you)\b", lowered):
            return f"I'm {config.ASSISTANT_NAME}! I'm your personal AI, here to help you out with whatever you need."

        if re.search(r"\b(what can you do|help|features|what do you do|how to use)\b", lowered):
            return "Oh, lots of things! I can open or close apps for you, play music, check the weather, look things up online, and just chat with you."

        if re.search(r"\b(hello|hi|hey|greetings|good morning|good afternoon|good evening)\b", lowered):
            return f"Hey there! I'm {config.ASSISTANT_NAME}. What's up?"

        if re.search(r"\b(thank you|thanks|thx|awesome|great job|well done)\b", lowered):
            return "You're very welcome! I'm always happy to help."

        if "joke" in lowered or "funny" in lowered:
            jokes = [
                "Why do programmers prefer dark mode? Because light attracts bugs!",
                "Why did the computer go to the doctor? Because it had a virus!",
                "There are 10 types of people in the world: those who understand binary, and those who don't!"
            ]
            return random.choice(jokes)

        # -------------------------------------------------------------
        # 2. SYSTEM TOOLS & ADVANCED CAPABILITIES
        # -------------------------------------------------------------

        # Screenshot Intent
        if "screenshot" in lowered or "capture screen" in lowered or "take a picture of screen" in lowered:
            return take_screenshot()

        # Wikipedia Knowledge Intent (e.g. "who is Albert Einstein on wikipedia", "search wikipedia for quantum computing")
        if "wikipedia" in lowered or lowered.startswith("who is") or lowered.startswith("what is a") or lowered.startswith("tell me about"):
            topic = re.sub(r"\b(search wikipedia for|on wikipedia|who is|what is a|what is|tell me about)\b", "", lowered, flags=re.IGNORECASE).strip()
            if topic:
                return search_wikipedia(topic)

        # System Resources & Battery Intent (e.g. "check cpu", "ram usage", "system resources", "battery")
        if any(k in lowered for k in ["battery", "cpu", "ram", "memory", "system resources", "system specs", "hardware"]):
            return get_system_resources()

        # News Headlines Intent (e.g. "read the news", "top news", "news headlines")
        if "news" in lowered or "headlines" in lowered:
            return get_news_headlines()

        # Volume Control Intent (e.g. "mute audio", "volume up", "volume down", "unmute")
        if "volume" in lowered or "mute" in lowered or "unmute" in lowered:
            if "mute" in lowered and "unmute" not in lowered:
                return control_system_volume("mute")
            elif "unmute" in lowered:
                return control_system_volume("unmute")
            elif "up" in lowered or "increase" in lowered or "raise" in lowered:
                return control_system_volume("up")
            elif "down" in lowered or "decrease" in lowered or "lower" in lowered:
                return control_system_volume("down")

        # Media Playback Intent (e.g. "play shape of you on youtube", "play lofi beats")
        if lowered.startswith("play") or "play on youtube" in lowered:
            query = re.sub(r"^(play|play on youtube|search and play)\s+", "", lowered, flags=re.IGNORECASE)
            query = query.replace("on youtube", "").strip()
            return play_media(query)

        # Application Close Intent (e.g. "close chrome", "kill notepad", "terminate spotify")
        if re.search(r"\b(close|kill|terminate|stop|exit)\b", lowered) and not re.search(r"\b(music|song|video|youtube)\b", lowered):
            match = re.search(r"\b(close|kill|terminate|stop|exit)\s+(.+)", lowered)
            if match:
                app_target = match.group(2).replace("the ", "").replace(" app", "").replace(" application", "").strip()
                return close_application(app_target)

        # Application Control Intent (e.g. "open notepad", "launch calculator", "start chrome")
        if re.search(r"\b(open|launch|start|run)\b", lowered):
            match = re.search(r"\b(open|launch|start|run)\s+(.+)", lowered)
            if match:
                app_target = match.group(2).replace("the ", "").replace(" app", "").replace(" application", "").strip()
                return open_application(app_target)

        # Web Search Intent (e.g. "search google for python", "look up weather forecast")
        if re.search(r"\b(search|search google for|google|look up)\b", lowered):
            query = re.sub(r"^(search google for|search for|search|google|look up)\s+", "", lowered, flags=re.IGNORECASE)
            return web_search(query)

        # Utility - Time & Date
        if "time" in lowered:
            return get_utility_info("time")
        if "date" in lowered or "day" in lowered:
            return get_utility_info("date")

        # Utility - Weather Intent
        if "weather" in lowered:
            loc_match = re.search(r"weather\s+(?:in|for|at)\s+([a-zA-Z\s]+)", lowered)
            location = loc_match.group(1).strip() if loc_match else ""
            return get_utility_info("weather", location)

        return ""
