from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
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
