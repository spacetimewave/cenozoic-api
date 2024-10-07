from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from repositories.database_repository import get_db, create_user, get_user_by_email_or_username, get_user_by_email, verify_password
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from repositories.auth_repository import create_access_token, verify_token
from pydantic import BaseModel
from typing import Optional
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Pydantic Models for Request and Response
class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str

class TokenResponse(BaseModel):
    message: str
    token_payload: dict

# Define the OAuth2PasswordBearer scheme, which tells FastAPI where to get the token from
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Configure CORS
origins = [
    "http://localhost:5173",  # Your React app URL
    # You can add more origins if needed
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # List of allowed origins
    allow_credentials=True,  # Allow cookies and credentials
    allow_methods=["*"],     # Allow all HTTP methods
    allow_headers=["*"],     # Allow all headers
)

# Signup Route
@app.post("/signup", response_model=UserResponse)
def signup(user: UserCreate, db: Session = Depends(get_db)):
    # Check if the email or username is already registered
    existing_user = get_user_by_email_or_username(db, user.email, user.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="Username or email is already registered")
    # Create the user
    new_user = create_user(db, user.username, user.email, user.password)
    return UserResponse(id=new_user.id, username=new_user.username, email=new_user.email)

# Root route for testing
@app.get("/root")
async def root():
    return {"message": "Hello World"}

# Login Route - Issue JWT token if login is successful
@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = get_user_by_email(db, form_data.username)
    # user = get_user_by_username(db, form_data.username)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid username or password")
    
    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid username or password")
    
    # Create a JWT token for the authenticated user
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer", "user_name": user.username, "user_mail": user.email}

# Protected route - Requires a valid JWT token
@app.get("/", response_model=TokenResponse)
async def root(token: str = Depends(oauth2_scheme)):
    payload = verify_token(token)
    if payload is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
    print(payload)
    return {"message": "Hello World", "token_payload": payload}

# if __name__ == "__main__":
#     uvicorn.run(app, host="0.0.0.0", port=8000)