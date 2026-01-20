from fastapi import FastAPI, HTTPException
from app.schemas import UserProfile
from app.agent import generate_financial_plan
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware # <--- 1. Import this

# Load API Key from .env
load_dotenv()

app = FastAPI()
origins = [
    "http://localhost:3000",      # React default port
    "http://127.0.0.1:3000",      # Alternative React URL
    "https://finance-advisor-gbgx.vercel.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,        # Whitelist these URLs
    allow_credentials=True,
    allow_methods=["*"],          # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],          # Allow all headers
)

@app.options("/generate-plan")
def generate_plan_options():
    return Response(status_code=200)
    
@app.post("/generate-plan")
def get_plan(user: UserProfile):
    try:
        # Convert Pydantic model to dict
        user_data = user.model_dump()
        
        # Call the Agent
        report = generate_financial_plan(user_data)
        
        return {"report": report}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))