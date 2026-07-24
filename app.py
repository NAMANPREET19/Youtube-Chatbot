from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from chain import ask_video


app = FastAPI()


class ChatRequest(BaseModel):

    video_id: str
    question: str



app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten to your extension's chrome-extension://<id> origin later if you want
    allow_methods=["*"],
    allow_headers=["*"],
)



@app.post("/chat")

def chat(data: ChatRequest):

    answer = ask_video(
        data.video_id,
        data.question
    )

    return {
        "answer": answer
    }