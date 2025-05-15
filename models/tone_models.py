from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict
from enum import Enum

class ToneLevel(str, Enum):
    FORMAL = "formal"
    SEMI_FORMAL = "semi-formal"
    INFORMAL = "informal"

class LanguageStyle(str, Enum):
    TECHNICAL = "technical"
    CONVERSATIONAL = "conversational"
    ACADEMIC = "academic"
    PROFESSIONAL = "professional"
    CREATIVE = "creative"

class EmotionalAppeal(str, Enum):
    RATIONAL = "rational"
    EMOTIONAL = "emotional"
    INSPIRATIONAL = "inspirational"
    HUMOROUS = "humorous"
    AUTHORITATIVE = "authoritative"

class ToneCharacteristics(BaseModel):
    tone: str = Field(..., description="Overall emotional tone (e.g., formal, casual, friendly)")
    language_style: LanguageStyle = Field(..., description="Language style")
    formality_level: ToneLevel = Field(..., description="Level of formality")
    address_style: str = Field(..., description="Forms of address (e.g., direct, indirect, personal)")
    emotional_appeal: EmotionalAppeal = Field(..., description="Type of emotional appeal")
    
    @validator('tone')
    def validate_tone(cls, v):
        valid_tones = ['formal', 'casual', 'friendly', 'professional', 'authoritative', 'warm', 'direct']
        if v.lower() not in valid_tones:
            raise ValueError(f'Tone must be one of: {", ".join(valid_tones)}')
        return v.lower()
    
    @validator('address_style')
    def validate_address_style(cls, v):
        valid_styles = ['direct', 'indirect', 'personal', 'impersonal', 'collective']
        if v.lower() not in valid_styles:
            raise ValueError(f'Address style must be one of: {", ".join(valid_styles)}')
        return v.lower()

class BrandInfo(BaseModel):
    brand_id: str = Field(..., description="Unique brand identifier")
    name: str = Field(..., description="Brand name")
    description: Optional[str] = Field(None, description="Brand description")
    created_at: str = Field(..., description="Timestamp of brand creation")

class ToneAnalysisResponse(BaseModel):
    signature: str = Field(..., description="The extracted tone signature")
    confidence: float = Field(..., description="Confidence score of the analysis", ge=0, le=1)
    characteristics: ToneCharacteristics = Field(..., description="Detailed tone characteristics")
    language_patterns: List[str] = Field(..., description="Identified language patterns")
    key_phrases: List[str] = Field(..., description="Characteristic phrases and expressions")

class TextAnalysisRequest(BaseModel):
    text: str = Field(..., min_length=10, description="Text to analyze")
    language: Optional[str] = Field("en", description="Language of the text")

class RewriteRequest(BaseModel):
    text: str = Field(..., min_length=10, description="Text to rewrite")
    signature: str = Field(..., description="Tone signature to apply")
    preserve_keywords: Optional[List[str]] = Field(default=[], description="Keywords to preserve in the rewrite")

class EvaluationRequest(BaseModel):
    brand_id: str = Field(..., description="Brand identifier")
    text: str = Field(..., min_length=10, description="Original text to evaluate")
    rewritten: str = Field(..., min_length=10, description="Rewritten text to evaluate")
    signature: str = Field(..., description="Tone signature used for rewriting")

class EvaluationResult(BaseModel):
    fluency: float = Field(..., ge=0, le=1, description="Fluency score")
    authenticity: float = Field(..., ge=0, le=1, description="Authenticity score")
    tone_alignment: float = Field(..., ge=0, le=1, description="Tone alignment score")
    readability: float = Field(..., ge=0, le=1, description="Readability score")
    overall_score: float = Field(..., ge=0, le=1, description="Overall evaluation score")
    strengths: List[str] = Field(..., description="List of strengths in the rewrite")
    suggestions: List[str] = Field(..., description="List of improvement suggestions")
    
    # New detailed metrics
    tone_characteristics_match: Dict[str, float] = Field(
        ...,
        description="Scores for each tone characteristic match (0-1)"
    )
    language_pattern_consistency: float = Field(
        ...,
        ge=0,
        le=1,
        description="Consistency score for language patterns"
    )
    brand_voice_alignment: float = Field(
        ...,
        ge=0,
        le=1,
        description="Alignment score with brand voice"
    )
    target_audience_appeal: float = Field(
        ...,
        ge=0,
        le=1,
        description="Appeal score for target audience"
    )
    detailed_feedback: Dict[str, List[str]] = Field(
        ...,
        description="Detailed feedback for each characteristic"
    )

class EvaluationResponse(BaseModel):
    evaluation_id: str = Field(..., description="Unique evaluation ID")
    brand_id: str = Field(..., description="Brand identifier")
    timestamp: str = Field(..., description="Evaluation timestamp")
    original_text: str = Field(..., description="Original text that was evaluated")
    rewritten_text: str = Field(..., description="Rewritten text that was evaluated")
    result: EvaluationResult = Field(..., description="Detailed evaluation results")

class RejectRequest(BaseModel):
    text: str = Field(..., min_length=10, description="Text to reject")
    reason: str = Field(..., min_length=10, description="Reason for rejection")
    category: Optional[str] = Field(None, description="Category of rejection")

class RejectResponse(BaseModel):
    status: str = Field(..., description="Status of the rejection")
    text: str = Field(..., description="Original text")
    reason: str = Field(..., description="Reason for rejection")
    suggestions: List[str] = Field(..., description="List of improvement suggestions")
    category: Optional[str] = Field(None, description="Category of rejection")

class TextRewriteRequest(BaseModel):
    text: str = Field(..., min_length=10, description="Text to rewrite")
    brand_id: Optional[str] = Field(None, description="Existing brand ID")
    brand_name: Optional[str] = Field(None, description="New brand name if creating a new brand")

class TextRewriteResponse(BaseModel):
    evaluation_id: str = Field(..., description="Unique evaluation ID")
    brand_info: BrandInfo = Field(..., description="Brand information")
    timestamp: str = Field(..., description="Timestamp of the rewrite and evaluation")
    original_text: str = Field(..., description="Original text that was rewritten")
    rewritten_text: str = Field(..., description="Rewritten text")
    result: EvaluationResult = Field(..., description="Evaluation results")

class SignatureResponse(BaseModel):
    brand_id: str = Field(..., description="Brand identifier")
    signature: str = Field(..., description="Tone signature")
    created_at: str = Field(..., description="Timestamp of signature creation")
    version: str = Field(..., description="Version of the signature")

class ErrorResponse(BaseModel):
    error: str = Field(..., description="Error message")
    code: str = Field(..., description="Error code")
    details: Optional[Dict] = Field(None, description="Additional error details") 