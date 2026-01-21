from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from app.schemas import UserProfile
from app.agent import generate_financial_plan

load_dotenv()

app = FastAPI()

# CORS MUST come before routes
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://finance-advisor-ggbx.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔑 Critical fix for Render + Vercel
@app.options("/{path:path}")
def options_handler(path: str):
    return Response(status_code=200)

@app.post("/generate-plan")
def get_plan(user: UserProfile):
    try:
        user_data = user.model_dump()
        report = generate_financial_plan(user_data)
        return {"report": report}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health():
    return {"status": "ok"}
