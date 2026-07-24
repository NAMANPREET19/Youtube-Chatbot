from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from youtube_transcript_api import AgeRestricted, YouTubeTranscriptApi, TranscriptsDisabled

from langchain_text_splitters import RecursiveCharacterTextSplitter


from langchain_community.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint


import os
from langchain_core.documents import Document
import requests
from langchain_huggingface import HuggingFaceEndpointEmbeddings
from langchain_community.vectorstores import FAISS
from dotenv import load_dotenv

load_dotenv()



llm = HuggingFaceEndpoint(
    repo_id="openai/gpt-oss-120b",
    huggingfacehub_api_token=os.getenv("huggingfacehub_api_token"),
    
    temperature=0.7,
)
chat_model = ChatHuggingFace(llm=llm)



chat_model2 = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.6,
    api_key=os.getenv("groq_api_key")
)


embeddings = HuggingFaceEndpointEmbeddings(
    repo_id="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
    huggingfacehub_api_token=os.getenv("huggingfacehub_api_token"),
    provider="hf-inference"
)


def get_vectorstore(video_id):

        try:
            api = YouTubeTranscriptApi()
            transcript_list = api.fetch(video_id, languages=["en", "hi", "en-US"])

            # Merge all caption lines into one continuous text first.
            # YouTube caption entries are only a few words each, so splitting
            # them individually (one Document per caption) leaves chunk_size
            # having no effect - every "chunk" ends up being a near-meaningless
            # 3-8 word fragment, which wrecks retrieval quality. We build one
            # running string instead, and remember where each caption started
            # so we can still tag each resulting chunk with a timestamp.
            full_text = ""
            offsets = []  # (char offset into full_text, start time in seconds)

            for item in transcript_list:
                offsets.append((len(full_text), item.start))
                full_text += item.text.strip() + " "

            splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
            raw_chunks = splitter.create_documents([full_text])

            chunks = []
            search_pos = 0

            for doc in raw_chunks:
                idx = full_text.find(doc.page_content, search_pos)
                if idx == -1:
                    idx = full_text.find(doc.page_content)
                if idx != -1:
                    search_pos = idx

                # timestamp of the last caption that starts at/before this chunk
                start_time = offsets[0][1] if offsets else 0
                for offset, ts in offsets:
                    if offset <= idx:
                        start_time = ts
                    else:
                        break

                chunks.append(
                    Document(
                        page_content=doc.page_content,
                        metadata={"start": start_time},
                    )
                )

            vector_store = FAISS.from_documents(chunks, embeddings)
            return vector_store
        except TranscriptsDisabled:
            return None
        except AgeRestricted:
            raise Exception("This video is age-restricted. Please choose another video.")
        
        