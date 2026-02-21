import os
from pathlib import Path

from fastapi import FastAPI, File, Request, UploadFile, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic_ai import Agent

from src.config import SETTINGS as _SETTINGS

UPLOAD_DIR = Path(__file__).parent.parent / "_temp_files"
os.makedirs(str(UPLOAD_DIR), exist_ok=True)

# ====================================================================================
#   Model configuration
# ====================================================================================


agent = Agent(
    _SETTINGS.model,
    instructions="Be concise, reply with short sentences.",
)

app = agent.to_web()


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
    full_prompt = []
    while True:
        try:
            user_prompt = await websocket.receive_text()
            file_content = None

            # If data is a filename (prefixed with "file:"), read the file
            if user_prompt.startswith("file:"):
                filename = user_prompt[5:]
                file_path = str(UPLOAD_DIR / filename)
                print(f"Trying to read from {file_path}")
                if os.path.exists(file_path):
                    with open(file_path, "r") as f:
                        file_content = {"filename": filename, "content": f.read()}
                    print("File OK")
                else:
                    await websocket.send_text(f"Error: File {filename} not found")
                    print("File not OK")
                continue

            full_prompt.append(user_prompt)

            if file_content:
                full_prompt.append(f"""
File content from {file_content["filename"]}: {file_content["content"]}
""")

            async with agent.run_stream(full_prompt) as result:
                async for message in result.stream_text():
                    await websocket.send_text(message)

            print(f""" 
                  
User prompt was:
                  
{user_prompt}
                  """)
        except WebSocketDisconnect:
            break
