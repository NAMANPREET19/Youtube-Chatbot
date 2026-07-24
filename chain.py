from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import (
    RunnableParallel,
    RunnablePassthrough,
    RunnableLambda
)

from langchain_classic.retrievers.multi_query import MultiQueryRetriever
import os
from transcript import get_vectorstore
from dotenv import load_dotenv

load_dotenv()

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.6,
    api_key=os.getenv("groq_api_key")
)


prompt = PromptTemplate(
    template="""
You are a helpful assistant.

Answer ONLY using the transcript below.
Each transcript excerpt starts with a timestamp in [MM:SS] or [HH:MM:SS] format.

When you use information from an excerpt, cite its timestamp inline right
after the relevant point, like this: "The speaker explains X [02:15]."
If multiple excerpts support your answer, cite each one where it's used.

If the answer isn't available,
say you don't know.

Answer in English.

Transcript:
{context}

Question:
{question}
""",
    input_variables=["context", "question"]
)


def seconds_to_timestamp(seconds):

    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60

    if h > 0:
        return f"{h:02}:{m:02}:{s:02}"

    return f"{m:02}:{s:02}"


def format_docs(docs):

    output = []

    for doc in docs:

        timestamp = seconds_to_timestamp(
            int(doc.metadata["start"])
        )

        output.append(
            f"[{timestamp}]\n{doc.page_content}"
        )

    return "\n\n".join(output)


def ask_video(video_id, question):

    vector_store = get_vectorstore(video_id)

    retriever = vector_store.as_retriever(
        search_type="mmr",
        search_kwargs={
            "k":4,
            "fetch_k":15,
            "lambda_mult":0.5
        }
    )

    multi = MultiQueryRetriever.from_llm(
        retriever=retriever,
        llm=llm
    )

    parser = StrOutputParser()

    parallel = RunnableParallel({
        "question": RunnablePassthrough(),
        "context": multi | RunnableLambda(format_docs)
    })

    chain = parallel | prompt | llm | parser

    return chain.invoke(question)