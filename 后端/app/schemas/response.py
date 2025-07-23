from pydantic import BaseModel

class BaseResponse(BaseModel):
    code:int
    msg:str
    data:dict={}

    @classmethod
    def success(cls,data=None):
        return cls(code=200,msg="success",data=data or {})

    @classmethod
    def error(cls,code=500,msg="error",data=None):
        return cls(code=code,msg=msg,data=data or {})

class UserStatsResponse(BaseModel):
    user_id: int
    user_name: str
    like_count: int
    follower_count: int
    following_count: int