from pydantic import BaseModel, Field


class GenerateAIRequest(BaseModel):
    tenant_id: int
    input_tokens: int = Field(ge=0)
    cached_input_tokens: int = Field(ge=0)
    output_tokens: int = Field(ge=0)
    reasoning_tokens: int = Field(ge=0)