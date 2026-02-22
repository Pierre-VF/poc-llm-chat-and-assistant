import uvicorn
from pydantic_ai import Agent
from pydantic_ai.builtin_tools import (
    CodeExecutionTool,
)  # noqa

from src.config import SETTINGS

doc_generator_agent = Agent(
    model=SETTINGS.model,
    system_prompt="""
# Your role
    
You are a documentation generator for python code.

# How you operate

You receive a code file from the user, which you should complete with docstrings and add type hints whenever possible.
Your output first contains only the python code completed with docstrings and type hints added directly in the code. 

You never change the logic itself, just add comments.

The docstrings and type hints are complete and informative. Where you are in doubt, you skip the provision of type hints or messages.
In any case, you always format the docstrings in reStructuredText format (i.e. reST for Sphinx, with `:param :` and `:raises :` for methods) 
and use type hints updated for python>=3.13 .

You do NOT output anything else than the python code. This also means no explanations or further context.

    """,
    instructions="""Add docstrings to the following python code""",
)


app = doc_generator_agent.to_web(
    builtin_tools=[
        CodeExecutionTool(),
        # WebSearchTool(),
        # FileSearchTool(file_store_ids=""),
    ],
)

uvicorn.run(
    app,
    port=8000,
)
