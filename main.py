import uvicorn

from src.app import agent, app

if False:
    uvicorn.run(app, port=8000)
else:
    from pydantic_ai.builtin_tools import (
        WebSearchTool,
    )  # noqa

    uvicorn.run(
        agent.to_web(
            builtin_tools=[
                # CodeExecutionTool(),
                WebSearchTool(),
                # FileSearchTool(file_store_ids=""),
            ]
        ),
        port=8000,
    )
