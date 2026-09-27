"""
ai_brain.py - Intent processing, LLM tool calling, and local fallback engine.
Integrates OpenAI / Gemini Function Calling to execute local Python actions based on natural language.
"""

import sys
import io
import json
import re

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import config
from tools import TOOLS_SCHEMA, execute_tool_call, open_application, web_search, get_utility_info, play_media

# Initialize OpenAI client if library & key are available
try:
    from openai import OpenAI
    HAS_OPENAI_LIB = True
except ImportError:
    HAS_OPENAI_LIB = False


class AIBrain:
    """
    Core AI reasoning component that interprets natural language user input,
    decides tool invocation via LLM Tool Calling, and formulates spoken responses.
    """
    def __init__(self):
        self.provider = config.LLM_PROVIDER
        self.openai_client = None

        if HAS_OPENAI_LIB and config.OPENAI_API_KEY:
            try:
                self.openai_client = OpenAI(api_key=config.OPENAI_API_KEY)
                print("[AI Brain]: Initialized OpenAI Function Calling engine.")
            except Exception as e:
                print(f"[AI Brain Notice]: Failed to initialize OpenAI client: {e}")

        if not self.openai_client:
            print("[AI Brain]: Operating in Rule-Based Local Fallback Mode (No API key required).")

    def process_command(self, user_input: str) -> str:
        """
        Main entry point for processing a user's spoken command.
        
        Args:
            user_input (str): The transcript text from Speech-to-Text.
        Returns:
            str: Final natural language response to be spoken by Text-to-Speech.
        """
        if not user_input:
            return ""

        # Use OpenAI tool calling if client is active
        if self.openai_client:
            return self._process_with_openai(user_input)
        else:
            # Fall back to high-performance local regex intent matcher
            return self._process_local_fallback(user_input)

    def _process_with_openai(self, user_input: str) -> str:
        """
        Processes intent using OpenAI's Function Calling API.
        """
        messages = [
            {
                "role": "system", 
                "content": (
                    f"You are {config.ASSISTANT_NAME}, an intelligent voice assistant. "
                    "Keep spoken responses concise, friendly, and direct. "
                    "Use available tool calls whenever the user requests web search, application opening, "
                    "weather, date/time info, or media playback."
                )
            },
            {"role": "user", "content": user_input}
        ]

        try:
            # Step 1: Send prompt + tool definitions to LLM
            response = self.openai_client.chat.completions.create(
                model=config.OPENAI_MODEL,
                messages=messages,
                tools=TOOLS_SCHEMA,
                tool_choice="auto",
                temperature=0.7
            )

            response_message = response.choices[0].message
            tool_calls = response_message.tool_calls

            # Step 2: Check if LLM requested tool execution
            if tool_calls:
                messages.append(response_message)  # Extend conversation history with assistant request

                for tool_call in tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)
                    
                    print(f"[Tool Calling]: Invoking '{function_name}' with args {function_args}")
                    tool_result = execute_tool_call(function_name, function_args)
                    print(f"[Tool Result]: {tool_result}")

                    # Step 3: Append tool output to conversation
                    messages.append({
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": tool_result
                    })

                # Step 4: Get final conversational response from LLM
                second_response = self.openai_client.chat.completions.create(
                    model=config.OPENAI_MODEL,
                    messages=messages
                )
                return second_response.choices[0].message.content

            # If no tool call was needed, return direct LLM response
            return response_message.content

        except Exception as e:
            print(f"[LLM Error]: API request failed: {e}. Falling back to local pattern engine.")
            return self._process_local_fallback(user_input)

    def _process_local_fallback(self, text: str) -> str:
        """
        Local pattern matcher that works immediately without any external LLM API key.
        Maps spoken intents directly to tool execution functions.
        """
        lowered = text.lower().strip()

        # 1. Media Playback Intent (e.g., "play shape of you on youtube", "play queen")
        if lowered.startswith("play") or "play on youtube" in lowered:
            query = re.sub(r"^(play|play on youtube|search and play)\s+", "", lowered, flags=re.IGNORECASE)
            query = query.replace("on youtube", "").strip()
            return play_media(query)

        # 2. Application Control Intent (e.g., "open notepad", "launch calculator", "start chrome")
        if re.search(r"\b(open|launch|start|run)\b", lowered):
            match = re.search(r"\b(open|launch|start|run)\s+(.+)", lowered)
            if match:
                app_target = match.group(2).replace("app", "").replace("application", "").strip()
                return open_application(app_target)

        # 3. Web Search Intent (e.g., "search google for python tutorial", "search for weather forecast")
        if re.search(r"\b(search|search google for|google|look up)\b", lowered):
            query = re.sub(r"^(search google for|search for|search|google|look up)\s+", "", lowered, flags=re.IGNORECASE)
            return web_search(query)

        # 4. Utility - Time / Date Intent
        if "time" in lowered:
            return get_utility_info("time")
        if "date" in lowered or "day" in lowered:
            return get_utility_info("date")

        # 5. Utility - Weather Intent (e.g., "what's the weather in London", "weather report")
        if "weather" in lowered:
            loc_match = re.search(r"weather\s+(?:in|for|at)\s+([a-zA-Z\s]+)", lowered)
            location = loc_match.group(1).strip() if loc_match else ""
            return get_utility_info("weather", location)

        # Default fallback response for generic conversation
        return f"I heard you say: '{text}'. You can ask me to open apps, search Google, check time or weather, or play songs on YouTube!"
