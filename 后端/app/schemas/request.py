from pydantic import BaseModel

class RegisterRequest(BaseModel):
    user_name:str
    password:str

class LoginRequest(BaseModel):
    user_name:str
    password:str

class PostRequest(BaseModel):
    title:str
    content:str

class CommentRequest(BaseModel):
    article_id:int
    article_content:str