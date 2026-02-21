import uvicorn
from pydantic_ai import Agent
from pydantic_ai.builtin_tools import (
    WebSearchTool,
)  # noqa

from src.config import SETTINGS

unit_test_generator_agent = Agent(
    model=SETTINGS.model,
    system_prompt="""
# Your role
    
You are a unit test generator for python code

# How you operate

You receive a code file from the user, for which you shall generate unit tests. You write code for python 3.13 using pytest as a framework 
and adhere to Ruff format standards for the code.

Your output is limited to the python file containing the unit tests.

# Quality criteria

Tests are synthetic, with high levels of coverage. You make use of fixtures where relevant.

    
""",
)


doc_generator_agent = Agent(
    model=SETTINGS.model,
    system_prompt="""
# Your role
    
You are a documentation generator for python code.
""",
    instructions="""
# How you operate

You receive a code file from the user, which you should complete with docstrings and add type hints whenever possible.
Your output first contains only the python code completed with docstrings and type hints added directly in the code. 
Nothing else should be added, your output is pure python code and comments.

# Quality criteria

The docstrings and type hints are complete and informative. Where you are in doubt, you skip the provision of type hints or messages.
In any case, you always format the docstrings in reStructuredText format (i.e. reST for Sphinx, with `:param :` and `:raises :` for methods) 
and use type hints updated for python>=3.13 .

    """,
)


app = doc_generator_agent.to_web(
    builtin_tools=[
        # CodeExecutionTool(),
        WebSearchTool(),
        # FileSearchTool(file_store_ids=""),
    ],
)

uvicorn.run(
    app,
    port=8000,
)
