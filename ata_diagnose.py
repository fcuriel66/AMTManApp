# Imports os & dotenv environment
import os
from dotenv import load_dotenv

# Imports required Langchain libraries
from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings, ChatOpenAI

# Imports diagnosis prompt
from prompts.tech_prompts import diagnose_prompt

# Load environment and api keys
load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")


def setup_rag_components():
    # Offline Phase

    # 1. Load
    loader = TextLoader("XML/ADM_AMM_1285_TREE.xml")
    #loader = PyPDFLoader("100-MPP1285-INTRODUCTION.PDF")
    docs = loader.load()
    print(f"Loaded {len(docs)} documents!")

    # 2. Split
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1500, chunk_overlap=200)
    chunks = text_splitter.split_documents(docs)
    print(f"Document split into {len(chunks)} chunks!")

    # 3. Embed & 4. Store
    print("Creating vector store")
    vectorstore = FAISS.from_documents(documents=chunks,
                                       embedding=OpenAIEmbeddings(
                                           model="text-embedding-3-small",
                                           api_key=API_KEY))
    print("Vector store created successfully")

    model = ChatOpenAI(api_key=API_KEY, model="gpt-5-mini")

    # setup retriever
    retriever = vectorstore.as_retriever()

    return retriever, model


if __name__ == "__main__":
    # Offline
    retriever, model = setup_rag_components()

    # Online
    while True:
        user_question = input("\nPlease briefly describe the symptoms of the failure or problem: ")
        if user_question.lower() == "none":
            print("Thank you for using AI_AMTMan.\nHasta la vista baby...!")
            break
        print("Thinking...")

        # 1. Retrieve
        retrieved_docs = retriever.invoke(user_question)

        context = "\n\n".join([doc.page_content for doc in retrieved_docs])

        # 2. Augment
        prompt_template = diagnose_prompt(user_question, context)

        # 3. Generate
        response = model.invoke(prompt_template)

        print("\nAnswer:\n", response.content)