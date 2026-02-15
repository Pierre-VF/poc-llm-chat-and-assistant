import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, File, Request, UploadFile, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic_ai import Agent
from pydantic_settings import BaseSettings


# Settings to start with
class Settings(BaseSettings):
    LLM_API_KEY: str = "not needed"
    LLM_URL: str
    LLM_MODEL: str


load_dotenv()
_SETTINGS = Settings()

UPLOAD_DIR = Path(__file__).parent.parent / "_temp_files"
os.makedirs(str(UPLOAD_DIR), exist_ok=True)

# ====================================================================================
#   Model configuration
# ====================================================================================

model_name = _SETTINGS.LLM_MODEL.lower()

if model_name.startswith("mistralai/"):
    from pydantic_ai.models.mistral import MistralModel
    from pydantic_ai.providers.mistral import MistralProvider

    model = MistralModel(
        _SETTINGS.LLM_MODEL,
        provider=MistralProvider(
            base_url=_SETTINGS.LLM_URL,
            api_key=_SETTINGS.LLM_API_KEY,
        ),
    )

elif model_name.startswith("openai/"):
    from pydantic_ai.models.openai import OpenAIChatModel
    from pydantic_ai.providers.openai import OpenAIProvider

    model = OpenAIChatModel(
        _SETTINGS.LLM_MODEL,
        provider=OpenAIProvider(
            base_url=_SETTINGS.LLM_URL,
            api_key=_SETTINGS.LLM_API_KEY,
        ),
    )

elif model_name.startswith("openai/"):
    from pydantic_ai.models.openai import OpenAIChatModel
    from pydantic_ai.providers.openai import OpenAIProvider

    model = OpenAIChatModel(
        _SETTINGS.LLM_MODEL,
        provider=OpenAIProvider(
            base_url=_SETTINGS.LLM_URL,
            api_key=_SETTINGS.LLM_API_KEY,
        ),
    )

else:
    raise EnvironmentError(f"Model not supported ({model_name})")

agent = Agent(
    model,
    instructions="Be concise, reply with short sentences.",
)

# ====================================================================================
#   App configuration
# ====================================================================================

app = FastAPI()

# Mount static files (CSS/JS)
app.mount(
    "/static",
    StaticFiles(directory=Path(__file__).parent / "static"),
    name="static",
)
templates = Jinja2Templates(directory=Path(__file__).parent / "templates")


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    file_path = str(UPLOAD_DIR / file.filename)
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())
    return {"filename": file.filename, "status": "uploaded"}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        try:
            user_prompt = await websocket.receive_text()
            file_content = None

            # If data is a filename (prefixed with "file:"), read the file
            if user_prompt.startswith("file:"):
                filename = user_prompt[5:]
                file_path = str(UPLOAD_DIR / filename)
                if os.path.exists(file_path):
                    with open(file_path, "r") as f:
                        file_content = {"filename": filename, "content": f.read()}
                else:
                    await websocket.send_text(f"Error: File {filename} not found")
                continue

            if file_content:
                user_prompt = f"""{user_prompt}

File content from {file_content["filename"]}: {file_content["content"]}
"""

            async with agent.run_stream(user_prompt) as result:
                async for message in result.stream_text():
                    await websocket.send_text(message)
        except WebSocketDisconnect:
            break
