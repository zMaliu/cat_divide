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

class LikeRequest(BaseModel):
    article_id:int

class FollowRequest(BaseModel):
    followed_id: int

class MessageRequest(BaseModel):
    touser_id: int
    content: str

class SessionRequest(BaseModel):
    touser_id: int