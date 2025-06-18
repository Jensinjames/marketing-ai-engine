from fastapi import FastAPI, APIRouter, HTTPException, Depends
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime
from enum import Enum
from emergentintegrations.llm.chat import LlmChat, UserMessage


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI(title="AI Marketing Asset Platform")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# OpenAI API Key
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is required")


# Enums
class AssetType(str, Enum):
    EMAIL_CAMPAIGN = "email_campaign"
    SOCIAL_MEDIA_AD = "social_media_ad"
    LANDING_PAGE = "landing_page"
    SALES_FUNNEL = "sales_funnel"
    BLOG_POST = "blog_post"
    PRESS_RELEASE = "press_release"

class PlanType(str, Enum):
    FREE = "free"
    STARTER = "starter"
    GROWTH = "growth"
    ENTERPRISE = "enterprise"


# Models
class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: Optional[str] = None
    name: Optional[str] = None
    plan: PlanType = PlanType.FREE
    credits: int = 100  # Free tier starts with 100 credits
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class Asset(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    title: str
    asset_type: AssetType
    content: str
    prompt_data: Dict[str, Any]
    credits_used: int = 1
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class CreditUsage(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    asset_id: str
    credits_consumed: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class GenerateAssetRequest(BaseModel):
    asset_type: AssetType
    business_name: str
    product_service: str
    target_audience: str
    tone: str = "professional"
    objectives: List[str] = []
    additional_context: Optional[str] = None

class GenerateAssetResponse(BaseModel):
    asset: Asset
    remaining_credits: int


# Asset generation prompts
ASSET_PROMPTS = {
    AssetType.EMAIL_CAMPAIGN: """Create a compelling email marketing campaign for {business_name}.

Product/Service: {product_service}
Target Audience: {target_audience}
Tone: {tone}
Objectives: {objectives}
Additional Context: {additional_context}

Please create:
1. An engaging subject line
2. Email body with clear call-to-action
3. Brief follow-up email suggestion

Format the response with clear sections and make it ready to use.""",

    AssetType.SOCIAL_MEDIA_AD: """Create high-converting social media ad copy for {business_name}.

Product/Service: {product_service}
Target Audience: {target_audience}
Tone: {tone}
Objectives: {objectives}
Additional Context: {additional_context}

Please create ad copy for:
1. Facebook/Instagram (with multiple variations)
2. LinkedIn (professional version)
3. Twitter/X (concise version)

Include suggested hashtags and call-to-action buttons.""",

    AssetType.LANDING_PAGE: """Create compelling landing page copy for {business_name}.

Product/Service: {product_service}
Target Audience: {target_audience}
Tone: {tone}
Objectives: {objectives}
Additional Context: {additional_context}

Please create:
1. Powerful headline and subheadline
2. Hero section copy
3. Benefits/features section
4. Social proof section
5. Strong call-to-action
6. FAQ section

Structure it as a complete landing page layout.""",

    AssetType.SALES_FUNNEL: """Create a complete sales funnel strategy for {business_name}.

Product/Service: {product_service}
Target Audience: {target_audience}
Tone: {tone}
Objectives: {objectives}
Additional Context: {additional_context}

Please create:
1. Lead magnet ideas and copy
2. Email sequence (5 emails)
3. Sales page structure
4. Upsell/cross-sell suggestions
5. Follow-up strategy

Provide actionable content for each stage.""",

    AssetType.BLOG_POST: """Create an engaging blog post for {business_name}.

Product/Service: {product_service}
Target Audience: {target_audience}
Tone: {tone}
Objectives: {objectives}
Additional Context: {additional_context}

Please create:
1. SEO-optimized title and meta description
2. Complete blog post with subheadings
3. Introduction, body, and conclusion
4. Call-to-action at the end
5. Suggested internal/external links

Make it informative and engaging for the target audience.""",

    AssetType.PRESS_RELEASE: """Create a professional press release for {business_name}.

Product/Service: {product_service}
Target Audience: {target_audience}
Tone: {tone}
Objectives: {objectives}
Additional Context: {additional_context}

Please create:
1. Compelling headline
2. Professional press release body
3. Company boilerplate
4. Contact information template
5. Distribution suggestions

Follow standard press release format and make it newsworthy."""
}


# Helper functions
async def get_or_create_user(email: str = "demo@example.com") -> User:
    """Get or create a demo user for MVP"""
    existing_user = await db.users.find_one({"email": email})
    if existing_user:
        return User(**existing_user)
    
    user = User(email=email, name="Demo User")
    await db.users.insert_one(user.dict())
    return user

async def consume_credits(user: User, credits: int) -> bool:
    """Consume credits for a user"""
    if user.credits < credits:
        return False
    
    # Update user credits
    user.credits -= credits
    user.updated_at = datetime.utcnow()
    await db.users.update_one(
        {"id": user.id}, 
        {"$set": {"credits": user.credits, "updated_at": user.updated_at}}
    )
    return True

async def generate_content_with_ai(prompt: str) -> str:
    """Generate content using OpenAI"""
    try:
        # Create a new chat instance for each generation
        chat = LlmChat(
            api_key=OPENAI_API_KEY,
            session_id=str(uuid.uuid4()),
            system_message="You are an expert marketing copywriter and strategist. Create compelling, professional marketing content that drives results."
        ).with_model("openai", "gpt-4o").with_max_tokens(4096)
        
        user_message = UserMessage(text=prompt)
        response = await chat.send_message(user_message)
        return response
    except Exception as e:
        logging.error(f"AI generation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"AI generation failed: {str(e)}")


# API Routes
@api_router.get("/")
async def root():
    return {"message": "AI Marketing Asset Platform API"}

@api_router.get("/user/profile")
async def get_user_profile():
    """Get current user profile (demo user for MVP)"""
    user = await get_or_create_user()
    return user

@api_router.post("/assets/generate", response_model=GenerateAssetResponse)
async def generate_asset(request: GenerateAssetRequest):
    """Generate a new marketing asset using AI"""
    # Get demo user
    user = await get_or_create_user()
    
    # Check credits
    credits_needed = 1
    if not await consume_credits(user, credits_needed):
        raise HTTPException(status_code=402, detail="Insufficient credits")
    
    # Generate prompt
    prompt_template = ASSET_PROMPTS[request.asset_type]
    objectives_str = ", ".join(request.objectives) if request.objectives else "increase engagement and conversions"
    
    formatted_prompt = prompt_template.format(
        business_name=request.business_name,
        product_service=request.product_service,
        target_audience=request.target_audience,
        tone=request.tone,
        objectives=objectives_str,
        additional_context=request.additional_context or "No additional context provided"
    )
    
    # Generate content with AI
    content = await generate_content_with_ai(formatted_prompt)
    
    # Create asset
    asset = Asset(
        user_id=user.id,
        title=f"{request.business_name} - {request.asset_type.value.replace('_', ' ').title()}",
        asset_type=request.asset_type,
        content=content,
        prompt_data=request.dict(),
        credits_used=credits_needed
    )
    
    # Save asset
    await db.assets.insert_one(asset.dict())
    
    # Log credit usage
    credit_usage = CreditUsage(
        user_id=user.id,
        asset_id=asset.id,
        credits_consumed=credits_needed
    )
    await db.credit_usage.insert_one(credit_usage.dict())
    
    # Get updated user credits
    updated_user = await get_or_create_user()
    
    return GenerateAssetResponse(asset=asset, remaining_credits=updated_user.credits)

@api_router.get("/assets", response_model=List[Asset])
async def get_assets():
    """Get all assets for the current user"""
    user = await get_or_create_user()
    assets = await db.assets.find({"user_id": user.id}).sort("created_at", -1).to_list(100)
    return [Asset(**asset) for asset in assets]

@api_router.get("/assets/{asset_id}", response_model=Asset)
async def get_asset(asset_id: str):
    """Get a specific asset"""
    asset = await db.assets.find_one({"id": asset_id})
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    return Asset(**asset)

@api_router.delete("/assets/{asset_id}")
async def delete_asset(asset_id: str):
    """Delete an asset"""
    result = await db.assets.delete_one({"id": asset_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Asset not found")
    return {"message": "Asset deleted successfully"}

@api_router.get("/dashboard/stats")
async def get_dashboard_stats():
    """Get dashboard statistics"""
    user = await get_or_create_user()
    
    # Get asset counts by type
    asset_counts = {}
    for asset_type in AssetType:
        count = await db.assets.count_documents({"user_id": user.id, "asset_type": asset_type.value})
        asset_counts[asset_type.value] = count
    
    total_assets = sum(asset_counts.values())
    credits_used_total = await db.credit_usage.count_documents({"user_id": user.id}) or 0
    
    return {
        "user": user,
        "total_assets": total_assets,
        "credits_used": credits_used_total,
        "asset_counts": asset_counts,
        "plan_limits": {
            "free": {"credits": 100, "assets": 50},
            "starter": {"credits": 500, "assets": 200},
            "growth": {"credits": 2000, "assets": 1000},
            "enterprise": {"credits": 10000, "assets": "unlimited"}
        }
    }


# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()