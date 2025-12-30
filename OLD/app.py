import os
from dotenv import load_dotenv
from langchain_community.document_loaders import TextLoader, PyPDFLoader

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from openai import embeddings

load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY")


def setup_rag_components():
    # Offline Phase

    # 1. Load
    #loader = TextLoader("rag_history.txt")
    loader = PyPDFLoader("Last/100-MPP1285-INTRODUCTION.PDF")
    docs = loader.load()
    print(f"Loaded {len(docs)} documents!")

    # 2. Split
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=3000, chunk_overlap=300)
    chunks = text_splitter.split_documents(docs)
    print(f"Document split into {len(chunks)} chunks!")

    # 3. Embed & 4. Store
    print("Creating vector store")
    vectorstore = FAISS.from_documents(documents=chunks,
                                       embedding=OpenAIEmbeddings(model="text-embedding-3-small", api_key=API_KEY))
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
        user_question = input("\nYour question: ")

        print("Thinking...")

        # 1. Retrieve
        retrieved_docs = retriever.invoke(user_question)

        context = "\n\n".join([doc.page_content for doc in retrieved_docs])

        # 2. Augment
        prompt_template = f"""You are an aircraft technician. 
        Answer the following question using your knowledge and the following context:

        {context}

        Question: {user_question}. Make sure to consider the whole Table 4, which is distributed in 3 pages of the
        document. Also print the whole Table 4.
        """

        # 3. Generate
        response = model.invoke(prompt_template)

        print("\nAnswer:\n", response.content)