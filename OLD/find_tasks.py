import os
from PDF.pdf_files import manual_files
from dotenv import load_dotenv
from langchain_community.document_loaders import TextLoader, PyPDFLoader

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
#from openai import embeddings

load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY")

PDF_FILES = manual_files()

def setup_rag_components2(pdf_files):
    # Offline Phase, Multiple files

    all_docs = []

    # 1. Load multiple PDFs
    for pdf_path in pdf_files:
        loader = PyPDFLoader(pdf_path)
        docs = loader.load()
        print(f"Loaded {len(docs)} documents from: {pdf_path}")
        all_docs.extend(docs)

    print(f"Total documents loaded: {len(all_docs)}")

    # 2. Split
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = text_splitter.split_documents(all_docs)
    print(f"All documents split into {len(chunks)} chunks!")

    # 3. Embed & 4. Store
    print("Creating vector store")
    vectorstore = FAISS.from_documents(
        documents=chunks,
        embedding=OpenAIEmbeddings(
            model="text-embedding-3-small",
            api_key=API_KEY
        )
    )
    print("Vector store created successfully")

    # LLM
    model2 = ChatOpenAI(api_key=API_KEY, model="gpt-5-mini")

    # Retriever
    retriever2 = vectorstore.as_retriever()

    return retriever2, model2


if __name__ == "__main__":
    # Offline

    retriever, model = setup_rag_components2(PDF_FILES)

    # Online
    while True:
        component_system = input("\nList the components or system for task list:\n")

        print("Thinking...")

        # 1. Retrieve
        retrieved_docs2 = retriever.invoke(component_system, k=6)

        context = "\n\n---".join([doc.page_content for doc in retrieved_docs2])
        #print(context)
        # 2. Augment
        prompt_template = f"""You are an experienced aircraft technician. 
        you will be provided with a comma separated list of components and an
        aircraft maintenance manual as context.
        Use your knowledge, the aircraft components and the context to
        list all the task numbers and its brief description.
        Make sure to only list the tasks for the components provided.
        Understand deeply the user's query. Identify how many different components or
        systems exist in it and then carefully select them from the context. 
        Components list:
        
        {component_system} 
        
        Context:
        
        {context}
        """

        # 3. Generate
        response = model.invoke(prompt_template)

        print("\nAnswer:\n", response.content)