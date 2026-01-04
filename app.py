import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import (
    ChatGoogleGenerativeAI,
    GoogleGenerativeAIEmbeddings
)
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

load_dotenv()

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "uploaded_pdfs")

# GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

GOOGLE_API_KEY = "AIzaSyB0FK5JoJ-HqmBFirphB7d5g6AcQohxHCA"

rag_chain = None   # 👈 global (important)


def build_rag():
    global rag_chain

    documents = []
    for file in os.listdir(UPLOAD_FOLDER):
        if file.endswith(".pdf"):
            loader = PyPDFLoader(os.path.join(UPLOAD_FOLDER, file))
            documents.extend(loader.load())

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    splits = text_splitter.split_documents(documents)

    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001",
        api_key=GOOGLE_API_KEY
    )

    vectorstore = FAISS.from_documents(splits, embeddings)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 4})

    prompt = ChatPromptTemplate.from_template(
        """
Answer the question using ONLY the context below.
If the answer is not in the context, say "I don't know".

Context:
{context}

Question:
{question}
"""
    )

    model = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash-lite",
        api_key=GOOGLE_API_KEY
    )

    rag_chain = (
        {
            "context": retriever | (lambda docs: "\n\n".join(d.page_content for d in docs)),
            "question": RunnablePassthrough()
        }
        | prompt
        | model
        | StrOutputParser()
    )


def ask_rag(question: str) -> str:
    if rag_chain is None:
        return "Please upload a document first."
    return rag_chain.invoke(question)
