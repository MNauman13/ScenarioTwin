from openai import OpenAI
from ..config import settings

# Single shared client for all agents.
# base_url points at LiteLLM proxy which handles provider routing.
_client = OpenAI(
    base_url=f"{settings.llm_gateway_url}/v1",
    api_key=settings.litellm_master_key,
)


def chat(
    model: str,
    system: str,
    user: str,
    *,
    json_mode: bool = False,
    temperature: float = 0.1,
    max_tokens: int = 512
) -> str:
    kwargs: dict = {}
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}

    response = _client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user}
        ],
        temperature=temperature,
        max_tokens=max_tokens,
        **kwargs,
    )
    return response.choices[0].message.content