# Streamlit Environment
import streamlit as st

# System & OS Environment
import os
from dotenv import load_dotenv
from dataclasses import dataclass

# Langchain libraries & Tools
from langchain.tools import tool
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver
#from langchain.agents.structured_output import ToolStrategy

# Self-made libraries, prompts and Auxiliary Functions
from symptoms_RAG import setup_rag_components
from find_tasks_efficient import load_rag_components, USER_WELCOME, extract_task_list
from prompts.tech_prompts import diagnose_prompt, ATA_chapters
from prompts.tech_prompts import find_task_prompt, SYSTEM_PROMPT
from database.models import init_db

from AUX.auxiliary_functions import gradient_text_html, find_pdf_from_task_numbers, save_history
from AUX.auxiliary_functions import get_all_users, load_history
import time

# Load environment variables
load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")

# Init Database and create tables. To be run only the first time
DB_PATH = "database/maintenance.db"
#init_db(DB_PATH)


@st.cache_data
def call_agent(maintenance_query: str):

    # --------------------------
    # Context Schema
    # --------------------------
    @dataclass
    class Context:
        user_id: str

    # --------------------------
    # RAG LLM Tools
    #---------------------------

    # Find tasks (RAG tool)
    @tool
    def find_tasks(components: str) -> str:
        """ finds tasks for systems or components responsible for the failure."""
        print("\nSearch Tasks RAG tool chosen. Thinking...\n")

        # ---- Use only once to create and load vectorstore (e.g. with new manual version)
        # build_and_save_vectorstore(PDF_FILES)

        # --- Use already saved vector embeddings
        retriever, model_tasks = load_rag_components()

        component_system = components
        if component_system.lower() == "none":
            return "Thank you for using AI_AMTMan.\nHasta la vista baby...!"
        print("Thinking...")

        # Retrieve of stored docs and Prompt Template
        retrieved_docs2 = retriever.invoke(component_system, k=4)
        context = "\n\n---".join(doc.page_content for doc in retrieved_docs2)
        prompt_template = find_task_prompt(component_system, context)

        # Invoking of response
        response_tasks = model.invoke(prompt_template)
        tasks_to_pdf = extract_task_list(response_tasks.content)
        find_pdf_from_task_numbers(tasks_to_pdf)
        return response_tasks.content


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
        print("Diagnostics RAG tool chosen. Thinking...")
        # 1. Retrieve
        retrieved_docs_srag = retriever_srag.invoke(user_question)
        context_srag = "\n\n".join([doc.page_content for doc in retrieved_docs_srag])

        # 2. Augment
        prompt_template_srag = diagnose_prompt(user_question, context_srag)

        # 3. Generate response
        rag_response = model_rag.invoke(prompt_template_srag)
        print(f"\nAnswer: \n {rag_response.content}")

        return f"\nAnswer: \n {rag_response.content}"


    # --------------------------
    # Auxiliary Tools in: PDF.auxiliary_functions
    #---------------------------


    # --------------------------
    # AI Model parameter definition
    # --------------------------
    model = ChatOpenAI(
        api_key=API_KEY,
        temperature=0,
        model="gpt-5-mini",
        reasoning_effort="low"
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

    # Return the assistant final message (response) or the history
    return history
    #return response


# ----------------------------
# STREAMLIT
# ---------------------------
# Streamlit Element Config
st.logo("/Users/fernandocuriel/PycharmProjects/RAG/XML/RWS logo.png", size="large")
#st.title(":blue[AI Aircraft Maintenance Agent]")

st.markdown(gradient_text_html, unsafe_allow_html=True)
st.caption("Aircraft Maintenance AI Agent")


# Sidebar selectbox
option = st.sidebar.selectbox("Choose an Aircraft:", ["EMB145/135", "*BE40*", "*EMB600*"])
st.write("Aircraft Type: ", option)

# Sidebar elements
st.sidebar.title(":grey[*EMB145/135 Regional Jet*]")
st.sidebar.caption("[EMB145 MPP Introduction](https://www.dropbox.com/scl/fi/kd6gkh65rz3ukmpk8zc6p/100-MPP1285-INTRODUCTION.PDF?rlkey=ogwkmtdraofqo24j8di2coy2y&dl=0)")

# Sidebar user selection and history loading --------------------------
st.sidebar.header("📂 User History")

users = get_all_users(DB_PATH)

if users:
    selected_user = st.sidebar.selectbox(
        "Select a user",
        users
    )

    if st.sidebar.button("Load History"):
        history_rows = load_history(selected_user, DB_PATH)

        st.session_state["loaded_history"] = history_rows
        st.session_state["selected_user"] = selected_user
else:
    st.sidebar.info("No users found yet.")




# Sidebar control
hide_ATA = st.sidebar.checkbox("*Show ATA Chapters* ")
hide_manual = st.checkbox("Instructions and Query Examples")
hide_directory = st.sidebar.checkbox("*Show saved PDF tasks files*")
contents = os.listdir('./PDF/AMM_EXTRACTED')

# Sidebar content
with st.sidebar:
    if hide_ATA:
        st.sidebar.write(ATA_chapters)
    if hide_directory:
        st.sidebar.write(":grey[*Saved Files in:*]")
        st.sidebar.write(":orange[==================================]")
        #st.sidebar.write(contents)
        for index in contents:
            st.sidebar.write(index, f":small[:grey[/ {index} - XX - *.PDF]]")

        st.sidebar.write(":orange[==================================]")


if hide_manual:
    st.write(USER_WELCOME)

# -------------
# Chat UI
# -------------
# Initialize chat history in session state if it doesn't exist
if "messages" not in st.session_state:
    st.session_state.messages = []

with st.chat_message("assistant", avatar=":material/smart_toy:"):
    st.write("*Welcome to AMTMan-E145, the AI Aircraft Maintenance Task Manager!*")

# Display chat messages from history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])




if prompt := st.chat_input("Please enter your maintenance query:"):
    with st.spinner("Choosing Tools...", show_time=False):
        time.sleep(2)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Run Agent and show its response
    agent_history = call_agent(prompt)
    channel_messages = agent_history["channel_values"]["messages"]
    for msg in channel_messages:
        st.session_state.messages.append({"role": "assistant",
                                          "content": f"""[{msg.type.upper()}]message
                                          \n\tTool call: [ {msg.name} ]\n:orange[{msg.content}]"""})

    # Save history of the user conversation (timestamped)
    user_id = "3"

    save_history(
        user_id=user_id,
        history=channel_messages
    )

    #st.write(channel_messages)

    st.rerun()


# Display DB loaded history----------------------------
st.write("🧾 Conversation History")

if "loaded_history" in st.session_state:
    for role, content, ts in st.session_state["loaded_history"]:
        if role == "human":
            st.markdown(f"**🧑‍🔧 User:** {content}")
        elif role == "ai":
            st.markdown(f"**🤖 Assistant:** {content}")
        st.caption(ts)
        st.divider()
else:
    st.info("Select a user from the sidebar to load history or make a new query.")
#-------------------------------