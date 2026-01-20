import os
from typing import TypedDict
from langgraph.graph import StateGraph, END
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv

# --- NEW: Import Google Gemini Integration ---
from langchain_google_genai import ChatGoogleGenerativeAI
load_dotenv()
# 1. SETUP ENVIRONMENT
# Replace 'AIza...' with your actual key from Step 1
# "gemini-1.5-flash" is fast and cheap; "gemini-1.5-pro" is smarter.
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.5
)

# 2. DEFINE THE STATE (The "Memory")
class AgentState(TypedDict):
    user_json: dict       # Raw input from user
    financial_health: dict # Calculated metrics
    final_report: str     # The output text

# 3. NODE 1: THE QUANT ANALYST (Pure Math - No AI)
def quant_analyst_node(state: AgentState):
    user = state["user_json"]
    
    # Calculate Total Income
    total_income = user["monthly_income_fixed"] + user["monthly_income_variable"]
    
    # Calculate Total Expenses
    total_expenses = (user["monthly_expenses_rent"] + 
                      user["monthly_expenses_needs"] + 
                      user["monthly_expenses_wants"])
    
    # Logic: Savings Rate
    savings = total_income - total_expenses
    savings_rate = (savings / total_income) * 100 if total_income > 0 else 0
    
    # Logic: Emergency Fund (6 months)
    emergency_target = total_expenses * 6
    
    # Logic: Debt-to-Income (DTI)
    total_debt_payments = sum([l["monthly_payment"] for l in user["liabilities"]])
    dti_ratio = (total_debt_payments / total_income) * 100 if total_income > 0 else 0
    
    health_metrics = {
        "monthly_surplus": savings,
        "savings_rate_percent": round(savings_rate, 2),
        "emergency_fund_target": emergency_target,
        "dti_ratio_percent": round(dti_ratio, 2)
    }
    
    return {"financial_health": health_metrics}

# 4. NODE 2: THE ADVISOR (Gemini AI Reasoning)
def advisor_node(state: AgentState):
    user = state["user_json"]
    metrics = state["financial_health"]
    
    system_prompt = """You are an elite Personal Finance Advisor. 
    Analyze the user's profile and the pre-calculated financial metrics.
    
    RULES:
    1. Be blunt but empathetic.
    2. If Savings Rate < 20%, warn them explicitly.
    3. If Debt-to-Income > 40%, prioritize debt payment over investing.
    4. Provide a step-by-step Action Plan based on their goal: {goal}
    
    USER METRICS:
    {metrics}
    
    USER PROFILE:
    {user}
    """
    
    prompt = ChatPromptTemplate.from_template(system_prompt)
    chain = prompt | llm
    
    response = chain.invoke({
        "goal": user["primary_goal"],
        "metrics": metrics,
        "user": user
    })
    
    return {"final_report": response.content}

# 5. BUILD THE GRAPH
workflow = StateGraph(AgentState)

workflow.add_node("quant_analyst", quant_analyst_node)
workflow.add_node("financial_advisor", advisor_node)

workflow.set_entry_point("quant_analyst")
workflow.add_edge("quant_analyst", "financial_advisor")
workflow.add_edge("financial_advisor", END)

app = workflow.compile()


# Function to run the agent
def generate_financial_plan(user_data: dict) -> str:
    result = app.invoke({"user_json": user_data})
    return result["final_report"]