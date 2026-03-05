#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "pydantic-ai[bedrock]>=0.0.14",
#   "fastapi>=0.115.0",
#   "uvicorn[standard]>=0.30.0",
#   "boto3>=1.35.0",
#   "python-dotenv>=1.0.0",
#   "pydantic>=2.0.0",
# ]
# ///


from __future__ import annotations

import boto3
import uvicorn
from dotenv import load_dotenv
from pydantic_ai import Agent
from pydantic_ai.models.bedrock import BedrockConverseModel
from pydantic_ai.providers.bedrock import BedrockProvider
from pydantic_settings import BaseSettings

# ── Configuration ──────────────────────────────────────────────────────────────


class Settings(BaseSettings):
    AWS_REGION: str = "eu-west-2"
    BEDROCK_MODEL: str = "anthropic.claude-3-7-sonnet-20250219-v1:0"
    PORT: int = 8000


load_dotenv()
_SETTINGS = Settings()

# ── Pydantic AI Agent setup ────────────────────────────────────────────────────


def create_bedrock_agent() -> Agent:
    """Create a Pydantic AI agent backed by AWS Bedrock."""
    bedrock_client = boto3.client("bedrock-runtime", region_name=_SETTINGS.AWS_REGION)
    model = BedrockConverseModel(
        model_name=_SETTINGS.BEDROCK_MODEL,
        provider=BedrockProvider(bedrock_client=bedrock_client),
    )

    agent = Agent(
        model=model,
        system_prompt=(
            "You are a helpful, knowledgeable assistant powered by AWS Bedrock. "
            "You provide clear, accurate, and thoughtful responses. "
            "When asked about your infrastructure, you can mention that you run "
            "via AWS Bedrock using Pydantic AI."
        ),
    )
    return agent


agent = create_bedrock_agent()


uvicorn.run(
    agent.to_web(),
    port=_SETTINGS.PORT,
    log_level="info",
    reload=False,
)
