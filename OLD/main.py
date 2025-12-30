import os
from dotenv import load_dotenv
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings, ChatOpenAI

load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY")

def setup_rag_components():
    # Offline Phase
    #1. Load
    loader = TextLoader("rag_history.txt")
    docs = loader.load()
    print(f"Loaded {len(docs)} documents!")

    #2. Split
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = text_splitter.split_documents(docs)
    print(f"Document split into {len(chunks)} chunks!")

    #3. Embed & Store
    vectorstore = FAISS.from_documents(documents=chunks, embedding=OpenAIEmbeddings(api_key=API_KEY))
    print("Vector store created successfully")

    model = ChatOpenAI(api_key=API_KEY)

    #4. Setup retriever
    retriever = vectorstore.as_retriever()
    return retriever, model


if __name__ == "__main__":
    #Offline
    retriever, model = setup_rag_components()

    #Online
    while True:
        user_question = input("\nYour question: ")
        print("thinking...")

        #1. Retrieve
        retrieved_docs = retriever.invoke(user_question)

        context = "\n\n".join([doc.page_content for doc in retrieved_docs])

        prompt_template = f"""Answer the question based ONLY on the following context: 
        {context}
        Question: {user_question}
        """

        #3. Generate
        response = model.invoke(prompt_template)

        print("Answering...")



#setup_rag_components()

