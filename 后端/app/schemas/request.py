from pydantic import BaseModel

class RegisterRequest(BaseModel):
    user_name:str
    password:str

class LoginRequest(BaseModel):
    user_name:str
    password:str

class PhoneLoginRequest(BaseModel):
    """手机号登录请求模型"""
    phone: str
    verification_code: str

class SendVerificationCodeRequest(BaseModel):
    """发送验证码请求模型"""
    phone: str

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
    name: str
    breed: str = None
    age: int = None
    gender: str = "unknown"
    description: str = None
    image_url: str = None  # 添加image_url字段

class CatUpdateRequest(BaseModel):
    name: str = None
    breed: str = None
    age: int = None
    gender: str = None
    description: str = None
    image_url: str = None  # 添加image_url字段