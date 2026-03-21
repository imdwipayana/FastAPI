from pydantic import BaseModel


class User(BaseModel):
    name:str
    emai: str
    account_id: str

    