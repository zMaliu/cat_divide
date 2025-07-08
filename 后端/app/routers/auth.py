from flask import Blueprint,request
from app.services.auth_service import AuthService
from app.schemas.response import BaseResponse

auth_hp=Blueprint("auth",__name__)

@auth_hp.route("/register",methods=["POST"])
def register():
    data=request.get_json()
    return AuthService.register(data["user_name"],data["password"]).dict()

@auth_hp.route("/login",methods=["POST"])
def login():
    data=request.get_json()
    return AuthService.login(data["user_name"],data["password"]).dict()