# Imports os & dotenv environment
import os
from dotenv import load_dotenv

from dataclasses import dataclass

from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain.tools import tool, ToolRuntime
from langgraph.checkpoint.memory import InMemorySaver
from langchain.agents.structured_output import ToolStrategy
from langchain_openai import OpenAIEmbeddings, ChatOpenAI

# Load environment and api keys
load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")


# Define system prompt
SYSTEM_PROMPT = """You are an expert weather forecaster.

You have access to two tools:

- get_weather_for_location: use this to get the weather for a specific location
- get_user_location: use this to get the user's location

If a user asks you for the weather, make sure you know the location. 
If you cannot tell the location from the question, 
use the get_user_location tool to find their location.
Always use your tools to answer the user question or say: I cannot answer"""

# Define context schema
@dataclass
class Context:
    """Custom runtime context schema."""
    user_id: str

# Define tools
@tool
def get_weather_for_location(city: str) -> str:
    """Get weather for a given city."""
    if city.lower() == "mexico city":
        return "it is raining in Mexico City"
    return f"It's always sunny in {city}!"

@tool
def get_user_location(runtime: ToolRuntime[Context]) -> str:
    """Retrieve user information based on user ID."""
    user_id = runtime.context.user_id
    return "Florida" if user_id == "1" else "SF"

# Configure model
# model = init_chat_model(
#     "gpt-5-mini",
#     temperature=0
#)
model = ChatOpenAI(
    temperature=0,
    model="gpt-5-mini",
    reasoning_effort="low"
)

# Define response format
# @dataclass
# class ResponseFormat:
#     """Response schema for the agent."""
#     # A punny response (always required)
#     punny_response: str
#     # Any interesting information about the weather if available
#     weather_conditions: str | None = None

# Set up memory
checkpointer = InMemorySaver()

# Create agent
agent = create_agent(
    model=model,
    system_prompt=SYSTEM_PROMPT,
    tools=[get_user_location, get_weather_for_location],
    context_schema=Context,
    #response_format=ToolStrategy(ResponseFormat),
    checkpointer=checkpointer
)

# Run agent
# `thread_id` is a unique identifier for a given conversation.
config = {"configurable": {"thread_id": "1"}}


while True:
    weather_query = input("How can I 'weather' you today? (pun intended): ")
    if weather_query.lower() == "none":
        print("No weather question... Ciao!")
        break
    response = agent.invoke(
        {"messages": [{"role": "user", "content": weather_query}]},
        config=config,
        context=Context(user_id="1")
    )
    #print(response['structured_response'])
    print(response)
    print(response["messages"][-1]["content"])