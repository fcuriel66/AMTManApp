# Imports os & dotenv environment
import os
from dotenv import load_dotenv
import ast

# Imports required Langchain libraries
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings, ChatOpenAI

# Loads maintenance manual pdf file directory
from PDF.pdf_files import manual_files

# Loads predefined prompts (find tasks, user welcome)
from prompts.tech_prompts import find_task_prompt, USER_WELCOME

load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")
PDF_FILES = manual_files()      # Gets all directory manual (MPP) references

FAISS_FOLDER = "faiss_index"       # folder where FAISS is stored
FAISS_INDEX_FILE = "index.faiss"   # binary FAISS index
FAISS_STORE_FILE = "index.pkl"     # metadata store

def user_welcome():
    print(USER_WELCOME)


def extract_task_list(text: str)->list:
    """ Last line reading of plain text (auxiliary, needs ast import)"""
    lines = [line.strip() for line in text.strip().splitlines() if line.strip()]
    last_line = lines[-1]          # get the final line
    task_list = ast.literal_eval(last_line)
    return task_list


# 1. Build and save vectorstore (needs to be run only when the MPP manual changes)

def build_and_save_vectorstore(pdf_files):
    all_docs = []

    # Load PDFs
    for pdf_path in pdf_files:
        loader = PyPDFLoader(pdf_path)
        docs = loader.load()
        print(f"Loaded {len(docs)} documents from: {pdf_path}")
        all_docs.extend(docs)

    print(f"Total documents loaded: {len(all_docs)}")

    # Split -------Tried from 500 to 3000 split with no noticeable difference noted
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = text_splitter.split_documents(all_docs)
    print(f"Documents split into {len(chunks)} chunks.")

    # Embed & Store
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small", api_key=API_KEY)
    vectorstore = FAISS.from_documents(chunks, embeddings)

    # Save to disk
    print("Saving FAISS index to disk...")
    vectorstore.save_local(FAISS_FOLDER)
    print("FAISS saved successfully!")


# 2. Load RAG components

def load_rag_components():
    # LOAD FAISS FROM DISK
    print("Loading FAISS index from disk...")
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small", api_key=API_KEY)
    vectorstore = FAISS.load_local(
        FAISS_FOLDER,
        embeddings,
        allow_dangerous_deserialization=True
    )
    print("FAISS index loaded successfully!")

    retriever = vectorstore.as_retriever()

    model = ChatOpenAI(api_key=API_KEY, model="gpt-5-mini")

    return retriever, model


# MAIN PROGRAM

if __name__ == "__main__":

    # -- Use only once to create and load vectorstore
    #build_and_save_vectorstore(PDF_FILES)
    # Uncomment the above line only for the very first run

    # -- Regular use
    retriever, model = load_rag_components()

    user_welcome()
    while True:

        component_system = input("\nList the components or system for task list:\n")
        if component_system.lower() == "none":
            print("Thank you for using AI_AMTMan.\nHasta la vista baby...!")
            break
        print("Thinking...")

        # Retrieve
        retrieved_docs2 = retriever.invoke(component_system, k=4)
        context = "\n\n---".join(doc.page_content for doc in retrieved_docs2)
        #print(context)

        # Prompt
        prompt_template = find_task_prompt(component_system, context)

        # Generate
        response = model.invoke(prompt_template)
        #print("\nAnswer:\n", response.content)
        print("\nAnswer:\n", response.content)

