from typing import Annotated

from pydantic import BaseModel, Field, StringConstraints


class SummarizeRequest(BaseModel):
    text: Annotated[str, StringConstraints(min_length=200, max_length=50000)]


class Summary(BaseModel):
    tldr: Annotated[
        str,
        StringConstraints(min_length=10, max_length=500),
        Field(description="A TL;DR summary of the text"),
    ]
    takeaways: Annotated[
        list[Annotated[str, StringConstraints(min_length=10, max_length=500)]],
        Field(min_length=5, max_length=5, description="5 key takeaways from the text"),
    ]
    social_post: Annotated[
        str,
        StringConstraints(min_length=10, max_length=280),
        Field(description="One-line, Twitter length summary of the text"),
    ]


class SummarizeResponse(BaseModel):
    summary: Summary
    model: str
    input_tokens: int
    output_tokens: int
