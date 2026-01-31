# -*- coding: utf-8 -*-
from pydantic import BaseModel
from typing import Optional

class BaseResponse(BaseModel):
    code:int
    msg:str
    data: Optional[dict] = None

    @classmethod
    def success(cls,data=None):
        return cls(code=200,msg="success",data=data if data is not None else {})

    @classmethod
    def error(cls,code=500,msg="error",data=None):
        return cls(code=code,msg=msg,data=data if data is not None else {})

class UserStatsResponse(BaseModel):
    user_id: int
    user_name: str
    like_count: int
    follower_count: int
    following_count: int












