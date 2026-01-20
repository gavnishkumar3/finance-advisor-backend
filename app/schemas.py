from pydantic import BaseModel
from typing import List, Optional

class Liability(BaseModel):
    type: str
    monthly_payment: float
    amount_remaining: float
    interest_rate: float

class Asset(BaseModel):
    type: str
    value: float

class UserProfile(BaseModel):
    age: int
    marital_status: str
    monthly_income_fixed: float
    monthly_income_variable: float = 0.0
    monthly_expenses_rent: float
    monthly_expenses_needs: float
    monthly_expenses_wants: float
    liabilities: List[Liability] = []
    assets: List[Asset] = []
    risk_tolerance: str
    primary_goal: str