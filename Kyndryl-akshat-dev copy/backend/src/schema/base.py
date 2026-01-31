from pydantic import BaseModel

# - # - # - # - # - # - # - # - # - # - # - # - # - # - # - # - # - # - # - # - 

class EndpointNameRequest(BaseModel):
    variable: str

class EndpointNameResponse(BaseModel):
    variable: str

# - # - # - # - # - # - # - # - # - # - # - # - # - # - # - # - # - # - # - # - 