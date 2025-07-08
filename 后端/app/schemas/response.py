from pydantic import BaseModel

class BaseResponse(BaseModel):
    code:int
    msg:str
    data:dict=None

    @classmethod
    def success(cls,data=None):
        return cls(code=200,msg="success",data=data)

    @classmethod
    def error(cls,code=500,msg="error"):
        return cls(code=code,msg=msg)