from dotenv import load_dotenv
from pydantic_ai.models import Model
from pydantic_settings import BaseSettings


# Settings to start with
class Settings(BaseSettings):
    LLM_API_KEY: str = "not needed"
    LLM_URL: str
    LLM_MODEL: str

    @property
    def model(self) -> Model:
        model_name = self.LLM_MODEL.lower()

        if model_name.startswith("mistralai/"):
            from pydantic_ai.models.mistral import MistralModel
            from pydantic_ai.providers.mistral import MistralProvider

            m = MistralModel(
                self.LLM_MODEL,
                provider=MistralProvider(
                    base_url=self.LLM_URL,
                    api_key=self.LLM_API_KEY,
                ),
            )

        elif model_name.startswith("openai/"):
            from pydantic_ai.models.openai import OpenAIChatModel
            from pydantic_ai.providers.openai import OpenAIProvider

            m = OpenAIChatModel(
                self.LLM_MODEL,
                provider=OpenAIProvider(
                    base_url=self.LLM_URL,
                    api_key=self.LLM_API_KEY,
                ),
            )

        else:
            raise EnvironmentError(f"Model not supported ({model_name})")

        return m


load_dotenv()
SETTINGS = Settings()
