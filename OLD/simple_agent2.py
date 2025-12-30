import os
from dotenv import load_dotenv
from dataclasses import dataclass

from langchain.tools import tool, ToolRuntime
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver
from langchain.agents.structured_output import ToolStrategy


# Load environment variables
load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")


# --------------------------
# SYSTEM PROMPT
# --------------------------
SYSTEM_PROMPT = """
You are an expert weather forecaster that answers sarcastically.

You have access to two tools:

- get_weather_for_location: use this to get the weather for a specific location
- get_user_location: use this to get the user's location

If the user asks for weather and no city is specified, 
use the get_user_location tool to determine the city location.
"""


# --------------------------
# CONTEXT SCHEMA
# --------------------------
@dataclass
class Context:
    user_id: str

#-------------------------------
# Define response format
#------------------------------
@dataclass
class ResponseFormat:
    """Response schema for the agent."""
    # A response (always required)
    punny_response: str
    # Any interesting information about the weather if available
    weather_conditions: str | None = None


# --------------------------
# TOOLS
# --------------------------
@tool
def get_weather_for_location(city: str) -> str:
    """Get weather for a given city."""
    if city.lower() == "mexico city":
        return "It is raining in Mexico City!"
    return f"It's always sunny in {city}!"


@tool
def get_user_location(runtime: ToolRuntime[Context]) -> str:
    """Retrieve user location based on user ID."""
    user_id = runtime.context.user_id
    return "Florida" if user_id == "1" else "San Francisco"


# --------------------------
# MODEL
# --------------------------
model = ChatOpenAI(
    api_key=API_KEY,
    temperature=0,
    model="gpt-5-mini",
    reasoning_effort="high",
    streaming=True
)


# --------------------------
# MEMORY
# --------------------------
checkpointer = InMemorySaver()


# --------------------------
# AGENT
# --------------------------
agent = create_agent(
    model=model,
    system_prompt=SYSTEM_PROMPT,
    tools=[get_user_location, get_weather_for_location],
    context_schema=Context,
    response_format=ToolStrategy(ResponseFormat),
    checkpointer=checkpointer
)

config = {"configurable": {"thread_id": "1"}}


# --------------------------
# MAIN LOOP
# --------------------------
while True:
    weather_query = input("\nHow can I 'weather' you today? (pun intended): ")

    if weather_query.lower() == "none":
        print("No weather question... Goodbye!")
        break

    response = agent.invoke(
        {"messages": [{"role": "user", "content": weather_query}]},
        config=config,
        context=Context(user_id="1")
    )

    # Print only the assistant final message
    print("\nAssistant:", response["structured_response"].punny_response, response["structured_response"].weather_conditions)
