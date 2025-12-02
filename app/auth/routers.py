from fastapi import APIRouter, Depends, HTTPException, Request, Response, Form
from fastapi.security import HTTPBasicCredentials, HTTPBasic
from db.utils import conn_to_db
import jwt
from models.model import User, User_registr
from auth.security import hash_password, verify_password, create_jwt
from auth.deps import check_valid_user_from_db_and_get_user, require_roles


router_auth = APIRouter(prefix='/auth')

@router_auth.post('/login')
def auth_and_set_jwt_in_cookie(res:Response, user: User = Depends(check_valid_user_from_db_and_get_user)):
    jwt_token = create_jwt(data={'username':user.username, 'roles':user.roles})
    res.set_cookie(key='jwt_personal_session_token', value=jwt_token)
    return {'message':f'access auth {user.username}'}


router_bd = APIRouter(prefix='/bd')

# @router_bd.post('/add_user', dependencies=[Depends(require_roles(['moderator']))])
# def add_user(user:HTTPBasicCredentials, con=Depends(conn_to_db)):
    
#     hash_psw = hash_password(user.password)
#     cursor = con.cursor()
#     cursor.execute('INSERT INTO users (username, hash_psw) VALUES (%s, %s)', (user.username, hash_psw))
#     id_user = cursor.fetchone()[0]
#     return {'message':f'user {user.username} is accessfully added with id {id_user}'}


@router_bd.post('/reg_user')
def reg_user(user:User_registr, con=Depends(conn_to_db)):
    
    if user.password != user.password_repeat:
        raise HTTPException(status_code=401, detail='passwords are not same')

    hash_psw = hash_password(user.password)
    cursor = con.cursor()
    cursor.execute('INSERT INTO users (username, hash_psw) VALUES (%s, %s)', (user.username, hash_psw))
    return {'message':f'user {user.username} is accessfully added'}
    

@router_bd.post("/update_roles", dependencies=[Depends(require_roles(["admin"]))])
def update_roles(
    username: str = Form(...),
    roles: list[str] = Form(...),
    conn = Depends(conn_to_db)
):
    cursor = conn.cursor()

    correct_roles = [s.strip() for s in roles[0].split(',')]
    
    cursor.execute(
        "UPDATE users SET roles = %s WHERE username = %s RETURNING id",
        (correct_roles, username)
    )
    user_row = cursor.fetchone()

    if not user_row:
        raise HTTPException(status_code=404, detail="User not found")

    return {"status": "ok", "username": username, "new_roles": roles}
