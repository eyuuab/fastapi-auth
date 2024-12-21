from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta

#secret key
SECRET_KEY = 'test'
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 30

#temp user databse
temp_user_db = {
    'eyobed': {
        'username': 'eyobed',
        'hashed_password': "$2b$12$K5x.QqXEuudV/tkvi9I3geX0sO./OPP3QapL.CvqKmPt2iHRxB4Ye"
    }
}

#token and password context

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

#verify password
def verify_password(plan_password, hashed_password):
    return pwd_context.verify(plan_password, hashed_password)

#get user
def get_user(username:str):
    user = temp_user_db.get(username)
    if user:
        return user

#authenticate user
def authenticate_user(username:str, password:str):
    user = get_user(username)
    if not user:
        return False
    if not verify_password(password, user['hashed_password']):
        return False
    return user

# create access token
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({'exp': expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

#Protected route dependency

def get_current_user(token:str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms = [ALGORITHM])
        username:str = payload.get('sub')
        if username is None:
            raise HTTPException(status_code=401, detail='Invalid Token')
        return username
    except JWTError:
        raise HTTPException(status_code=401, detail='Invalid Token')