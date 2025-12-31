# System & Environment
import os
from dotenv import load_dotenv
from dataclasses import dataclass

# Langchain libraries & Tools
from langchain.tools import tool, ToolRuntime
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver
#from langchain.agents.structured_output import ToolStrategy

# Self-made libraries, prompts and Auxiliary Functions
from symptoms_RAG import setup_rag_components
from find_tasks_efficient import load_rag_components, user_welcome, extract_task_list
from prompts.tech_prompts import diagnose_prompt
from prompts.tech_prompts import find_task_prompt, SYSTEM_PROMPT
from printing import print_pretty_history
from link_extract import extract_links_by_text, extract_chapter, copy_pdf_list

# Load environment variables
load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")


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
        tasks_to_pdf = extract_task_list(response_tasks.content)
        find_pdf_from_task_numbers(tasks_to_pdf)
        return f"Tasks found:  {response_tasks.content}"


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

        return f"\nAnswer:\n, {rag_response.content}"


    # --------------------------
    # Auxiliary Tools
    #---------------------------

    def find_pdf_from_task_numbers(task_numbers: list):
        """ Find PDF files from a list of task numbers."""

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
    # checkpointer history
    history = checkpointer.get(config)

    # Return the assistant final message or the history
    # (response["messages"][-1].content or history)

    return history
    # print("HISTORY: ", history["channel_values"]["messages"])
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
        maintenance_query = input("\nPlease enter your maintenance query: ")
        print(f"\nChoosing tool...\n")

        if maintenance_query.lower() == "none":
            print("No question... Goodbye!")
            break
        main()