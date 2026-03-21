from pydantic import BaseModel


class User(BaseModel):
    name:str
    email: str
    account_id: int

user = User(name='Jack', email='jack@game.com', account_id=1234)

print(user)
print(user.email)
print(user.name)