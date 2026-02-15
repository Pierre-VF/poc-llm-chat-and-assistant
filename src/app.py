import os
from pathlib import Path

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic_ai import Agent
from pydantic_ai.models.mistral import MistralModel
from pydantic_ai.providers.mistral import MistralProvider

os.environ["MISTRAL_API_KEY"] = "not needed"

app = FastAPI()

# Mount static files (CSS/JS)
app.mount(
    "/static", StaticFiles(directory=Path(__file__).parent / "static"), name="static"
)
templates = Jinja2Templates(directory=Path(__file__).parent / "templates")

# Configure the model to point to your self-hosted Mistral endpoint
model = MistralModel(
    "mistralai/ministral-3-3b",
    provider=MistralProvider(base_url="http://172.24.112.1:1234"),
)
agent = Agent(
    model,
    instructions="Be concise, reply with one sentence.",
)


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        try:
            user_prompt = await websocket.receive_text()
            async with agent.run_stream(user_prompt) as result:
                async for message in result.stream_text():
                    await websocket.send_text(message)
        except WebSocketDisconnect:
            break
