import asyncio
import os
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from copilot import CopilotClient
from copilot.generated.session_events import (
    AssistantMessageData,
    AssistantReasoningData,
    ToolExecutionStartData,
)
from copilot.session import PermissionHandler

BLUE = "\033[34m"
RESET = "\033[0m"

app = FastAPI()
client = None
session = None

class ChatRequest(BaseModel):
    message: str

def on_event(event):
    output = None
    match event.data:
        case AssistantReasoningData() as data:
            output = f"[reasoning: {data.content}]"
        case ToolExecutionStartData() as data:
            output = f"[tool: {data.tool_name}]"
    if output:
        print(f"{BLUE}{output}{RESET}")

@app.on_event("startup")
async def startup():
    global client, session
    
    # Explicitly grab the token from the environment
    token = os.getenv("COPILOT_GITHUB_TOKEN")
    
    if not token:
        print("ERROR: COPILOT_GITHUB_TOKEN is missing from environment variables!")
    
    # Pass the token explicitly to the client
    client = CopilotClient(
        github_token=token,
        use_logged_in_user=False
    )
    
    await client.start()
    session = await client.create_session(on_permission_request=PermissionHandler.approve_all)
    session.on(on_event)
    print("Copilot Session Started.")

@app.get("/", response_class=HTMLResponse)
async def serve_ui():
    with open("index.html", "r") as f:
        return f.read()

@app.post("/chat")
async def chat_endpoint(req: ChatRequest):
    global session
    reply = await session.send_and_wait(req.message)
    assistant_output = "Error: No response generated"
    
    if reply:
        match reply.data:
            case AssistantMessageData() as data:
                assistant_output = data.content
                
    return {"reply": assistant_output}