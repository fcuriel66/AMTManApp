import os
from dotenv import load_dotenv
from dataclasses import dataclass

from langchain.tools import tool, ToolRuntime
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver
from langchain.agents.structured_output import ToolStrategy

from symptoms_RAG import setup_rag_components
from find_tasks_efficient import load_rag_components, user_welcome
from prompts.tech_prompts import diagnose_prompt
from prompts.tech_prompts import find_task_prompt
from printing import print_pretty_history
from link_extract import extract_links_by_text, extract_chapter, copy_pdf_list

# Load environment variables
load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")


# --------------------------
# System Prompt
# --------------------------

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
• Make sure to comply if the user query explicitly tells you not to use a tool.
• If the first tool you choose is find_tasks. Call that tool and present the answer to the user.
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
        # (WHEN UNCOMMENTED, LINE BELOW CREATES INFINITE RAG CALLING LOOP)
        #systems_components: str | None = None

    # --------------------------
    # RAG LLM Tools
    #---------------------------

    # Find tasks (RAG tool)
    @tool
    def find_tasks(components: str) -> str:
        """ finds tasks for systems or components responsible for the failure."""
        print("\nSearch Tasks RAG tool chosen. Thinking...\n")

        # ---- Use only once to create and load vectorstore
        # build_and_save_vectorstore(PDF_FILES)
        # ---- Uncomment the above line only for the very first run

        # --- Use with saved vector embeddings
        retriever, model_tasks = load_rag_components()

        component_system = components
        if component_system.lower() == "none":
            return "Thank you for using AI_AMTMan.\nHasta la vista baby...!"
        print("Thinking...")

        # Retrieve of stored docs and Prompt Template
        retrieved_docs2 = retriever.invoke(component_system, k=4)
        context = "\n\n---".join(doc.page_content for doc in retrieved_docs2)
        # print(context)     --------Used for debugging only
        prompt_template = find_task_prompt(component_system, context)

        # Invoking of response
        response_tasks = model.invoke(prompt_template)
        #print("\nAnswer:\n", response_tasks.content)
        return f"Tasks found:  {response_tasks.content}"
        #return response_tasks.content


    # Symptoms diagnostic (RAG tool)
    @tool
    def symptoms_rag(symptoms_user: str) -> str:
        """
        Use the symptoms_user to determine the most likely cause of the problem.
        """
        # ----- Offline RAG components setup (file reading, splitting, embedding)
        retriever_srag, model_rag = setup_rag_components()

        # ----- Online (Retrieve, Augment, Generate)
        user_question = symptoms_user
        if user_question.lower() == "none":
            return "Thank you for using AI_AMTMan.\nHasta la vista baby...!"

        print("Diagnostics RAG tool chosen. Thinking...\n")

        # 1. Retrieve
        retrieved_docs_srag = retriever_srag.invoke(user_question)
        context_srag = "\n\n".join([doc.page_content for doc in retrieved_docs_srag])

        # 2. Augment
        prompt_template_srag = diagnose_prompt(user_question, context_srag)

        # 3. Generate response
        rag_response = model_rag.invoke(prompt_template_srag)
        print(f"\nAnswer:\n, {rag_response.content}")
        #test_tasks = ["21-51-03/400", "21-51-03-000-801-A", "21-00-00/200", "21-00-00-860-801-A"]
        return f"\nAnswer:\n, {rag_response.content}"

    # --------------------------
    # Auxiliary Tools
    #---------------------------

    # Extract PDF MPP files from task list tool
    @tool
    def find_pdf_from_task_numbers(task_numbers: list):
        """ Find PDF files from a list of task numbers."""
        # List of task numbers (extracted by AI Agent?)
        #task_numbers = ["21-51-03/400", "21-51-03-000-801-A", "21-00-00/200", "21-00-00-860-801-A"]

        # Extraction of chapter number to put in the search path
        tasks_chapter = extract_chapter(task_numbers)

        # Extraction of the links in pdf TOC chapter files associated with the text of tasks in task_num list
        matches = extract_links_by_text(f"PDF/025-MPP1285_{tasks_chapter}-TOC.PDF", task_numbers)

        # Copy selected PDF files from MPP original directory to single working directory (AMM_EXTRACTED)
        result = copy_pdf_list(
            matches,
            destination_dir="/Users/fernandocuriel/PycharmProjects/RAG/PDF/AMM_EXTRACTED/" + f"{tasks_chapter}",
            base_dir="/PDF"
        )

        print(f"Copied in ../AMM_EXTRACTED/{tasks_chapter}:")
        for f in result["copied"]:
            print("  ✓", f)

        print("\nMissing:")
        for f in result["missing"]:
            print("  ✗", f)

        return result


    # --------------------------
    # AI Model parameter definition
    # --------------------------
    model = ChatOpenAI(
        api_key=API_KEY,
        temperature=0,
        model="gpt-5-mini",
        reasoning_effort="medium"
    )

    # --------------------------
    # MEMORY
    # --------------------------
    checkpointer = InMemorySaver()


    # --------------------------
    # AGENT CREATION
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

    #--------------------
    # AGENT INVOCATION
    #--------------------

    response = agent.invoke(
        {"messages": [{"role": "user", "content": maintenance_query}]},
        config=config,
        context=Context(user_id="1")
    )
    history = checkpointer.get(config)                  # checkpointer history
    # Print only the assistant final message or history

    #print("HISTORY: ", history["channel_values"]["messages"])
    return history
    #return response["messages"][-1].content
    #return "\nAssistant:", response["structured_response"].rag_response
    #return response["structured_response"].rag_response


def main():
    #print(call_agent(maintenance_query))                   # final agent response only
    print_pretty_history(call_agent(maintenance_query))     # history answer


if __name__ == "__main__":

    # --------------------------
    # MAIN LOOP
    # --------------------------
    user_welcome()

    while True:
        maintenance_query = input("\nHow can I help you today?: ")
        print(f"\nChoosing tool...\n")

        if maintenance_query.lower() == "none":
            print("No question... Goodbye!")
            break
        main()