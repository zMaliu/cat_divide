# -*- coding: utf-8 -*-
from pydantic import BaseModel

class RegisterRequest(BaseModel):
    user_name:str
    password:str

class LoginRequest(BaseModel):
    user_name:str
    password:str

class PostCreateRequest(BaseModel):
    title: str
    content: str

class PostUpdateRequest(BaseModel):
    title: str
    content: str

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

class UnfollowRequest(BaseModel):
    followed_id: int

class CatCreateRequest(BaseModel):
    cat_name: str
    cat_breed: str = None
    cat_age: int = None
    cat_gender: str = "unknown"
    cat_description: str = None
    cat_image_url: str = None 

class CatUpdateRequest(BaseModel):
    cat_name: str = None
    cat_breed: str = None
    cat_age: int = None
    cat_gender: str = None
    cat_description: str = None
    cat_image_url: str = None  











