import os
from dotenv import load_dotenv
from dataclasses import dataclass

from langchain.tools import tool, ToolRuntime
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver
from langchain.agents.structured_output import ToolStrategy

from symptoms_RAG import setup_rag_components
from find_tasks_efficient import load_rag_components
from prompts.tech_prompts import diagnose_prompt

# Load environment variables
load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")


# --------------------------
# System Prompt

SYSTEM_PROMPT = """
You are an expert aircraft maintenance assistant.

Your role is extremely narrow: you may ONLY decide which one of the two available tools to call in order to answer the user’s request.

You have access to the following tools:

1. symptoms_rag  
   - Use this tool when the user describes aircraft symptoms, abnormalities, failures, 
    or operational problems, and is seeking diagnosis or likely causes.

2. find_tasks  
   - Use this tool when the user asks for maintenance tasks, task numbers, procedures, 
    or work instructions related to specific aircraft systems or components.

RULES OF OPERATION (MANDATORY):

• Choose one tool based on the user query.   
• If the first tool you choose  is find_tasks. Call that tool and present the answer to the user.
• If the first tool you choose is symptoms_rag, call that tool and examine the answer.
• Identify in that answer one system component and call the find_tasks tool, 
    present the answer to the user and STOP.
• NEVER explain your reasoning unless asked explicitly.   

YOUR STOP CONDITION (CRITICAL):

The stop condition is met the moment the find_tasks tool returns any output.  
Once this happens, your job is complete, and you must only show the tool’s response verbatim.

Your overall goal:  
Route the user’s query to the correct tool and terminate as soon as a find_tasks tool reply is available.

"""
def call_agent(maintenance_query: str):

    # --------------------------
    # Context Schema
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
        # A response from the RAG tools (always required)
        rag_response: str
        # list of systems or components if available in the response
        # (WHEN UNCOMMENTED CREATES INFINITE RAG CALLING LOOP)
        #systems_components: str | None = None


    # --------------------------
    # Tools definitions
    #---------------------------

    # Find tasks RAG tool
    @tool
    def find_tasks(components: str) -> str:
        """ finds tasks for systems or components responsible for the failure."""
        print("\nSearch Tasks RAG tool chosen. Thinking...\n")

        return f"Tasks found:  {components}"

    #------------------------------------
    # DIAGNOSTICS from symptoms RAG tool
    @tool
    def symptoms_rag(symptoms_user: str) -> str:
        """
        Use the symptoms_user to determine the most likely cause of the problem.
        """
        # Offline
        retriever_srag, model_rag = setup_rag_components()

        # Online

        user_question = symptoms_user
        # input("\nPlease briefly describe the symptoms of the failure or problem: ")
        if user_question.lower() == "none":
            return "Thank you for using AI_AMTMan.\nHasta la vista baby...!"

        print("Diagnostics RAG chosen. Thinking...\n")

        # 1. Retrieve
        retrieved_docs_srag = retriever_srag.invoke(user_question)
        context_srag = "\n\n".join([doc.page_content for doc in retrieved_docs_srag])

        # 2. Augment
        prompt_template_srag = diagnose_prompt(user_question, context_srag)

        # 3. Generate
        rag_response = model_rag.invoke(prompt_template_srag)
        print(f"\nAnswer:\n, {rag_response.content}")

        return f"\nAnswer:\n, {rag_response.content}"

    # --------------------------
    # AI Model parameter definition
    # --------------------------
    model = ChatOpenAI(
        api_key=API_KEY,
        temperature=0,
        model="gpt-5-mini",
        reasoning_effort="high"
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
        tools=[find_tasks, symptoms_rag],
        context_schema=Context,
        #response_format=ToolStrategy(ResponseFormat),
        checkpointer=checkpointer
    )

    config = {"configurable": {"thread_id": "1"}}
    #----------------
    # Invoke agent
    #-----------------
    response = agent.invoke(
        {"messages": [{"role": "user", "content": maintenance_query}]},
        config=config,
        context=Context(user_id="1")
    )
    # Print only the assistant final message
    print("\nAssistant:\n", response["messages"][-1].content)
    return response["messages"][-1].content
    #return "\nAssistant:", response["structured_response"].rag_response
    #return response["structured_response"].rag_response

    #print("\n", response["structured_response"].systems_components)

def main():
    call_agent(maintenance_query)


if __name__ == "__main__":

    # --------------------------
    # MAIN LOOP
    # --------------------------
    while True:
        maintenance_query = input("\nHow can I help you today?: ")
        print(f"\nChoosing tool...\n")

        if maintenance_query.lower() == "none":
            print("No question... Goodbye!")
            break
        main()

    # Print only the assistant final message
    # print("\nAssistant:\n", response["messages"][-1].content)

    #print("\nAssistant:", response["structured_response"].rag_response)
    #print("\n",response["structured_response"].systems_components)