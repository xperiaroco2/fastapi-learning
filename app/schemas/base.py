from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

SHARED_CONFIG = ConfigDict(
    alias_generator=to_camel,
    populate_by_name=True
)

class BaseRequestDTO(BaseModel):
    model_config = ConfigDict(
        **SHARED_CONFIG,
        extra="forbid",
        str_strip_whitespace=True,
    )

class BaseResponseDTO(BaseModel):
    model_config = ConfigDict(
        **SHARED_CONFIG,
        from_attributes=True,
    )