from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from controllers.tone_controller import ToneController
from models.tone_models import (
    TextAnalysisRequest,
    ToneAnalysisResponse,
    RewriteRequest,
    EvaluationRequest,
    EvaluationResponse,
    RejectRequest,
    RejectResponse,
    SignatureResponse,
    ErrorResponse,
    TextRewriteRequest,
    TextRewriteResponse
)
from typing import Optional

router = APIRouter(
    prefix="/tone",
    tags=["Tone Analysis"],
    responses={
        400: {"model": ErrorResponse, "description": "Bad Request"},
        404: {"model": ErrorResponse, "description": "Not Found"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"}
    }
)

controller = ToneController()

@router.post("/analyze/text", response_model=ToneAnalysisResponse)
async def analyze_text_endpoint(request: TextAnalysisRequest):
    """
    Analyze the tone of a given text.
    
    - **text**: The text to analyze (minimum 10 characters)
    - **language**: Optional language code (default: "en")
    
    Returns a tone signature and confidence score.
    """
    return await controller.analyze_text(request)

@router.post("/analyze/document", response_model=ToneAnalysisResponse)
async def analyze_document_endpoint(file: UploadFile = File(...)):
    """
    Analyze the tone of a Word document.
    
    - **file**: Word document (.docx) to analyze
    
    Returns a tone signature and confidence score.
    """
    return await controller.analyze_document(file)

@router.post("/rewrite")
async def rewrite_text_endpoint(request: RewriteRequest):
    """
    Rewrite text according to a tone signature.
    
    - **text**: Text to rewrite (minimum 10 characters)
    - **signature**: Tone signature to apply
    - **preserve_keywords**: Optional list of keywords to preserve
    
    Returns the rewritten text.
    """
    return await controller.rewrite_text(request)

@router.post("/evaluate", response_model=EvaluationResponse)
async def evaluate_text_endpoint(request: EvaluationRequest):
    """
    Evaluate rewritten text against original and signature.
    
    - **original**: Original text
    - **rewritten**: Rewritten text
    - **signature**: Tone signature used
    
    Returns detailed evaluation results.
    """
    return await controller.evaluate_text(request)

@router.get("/signature/{brand_id}", response_model=SignatureResponse)
async def get_signature_endpoint(brand_id: str):
    """
    Get stored signature for a brand.
    
    - **brand_id**: Brand identifier
    
    Returns the stored signature with metadata.
    """
    return await controller.get_signature(brand_id)

@router.post("/signature/{brand_id}", response_model=SignatureResponse)
async def store_signature_endpoint(brand_id: str, signature: str):
    """
    Store a signature for a brand.
    
    - **brand_id**: Brand identifier
    - **signature**: Tone signature to store
    
    Returns the stored signature with metadata.
    """
    return await controller.store_signature(brand_id, signature)

@router.get("/evaluation/{eval_id}", response_model=EvaluationResponse)
async def get_evaluation_endpoint(eval_id: str):
    """
    Get stored evaluation by ID.
    
    - **eval_id**: Evaluation identifier
    
    Returns the stored evaluation results.
    """
    return await controller.get_evaluation(eval_id)

@router.post("/reject", response_model=RejectResponse)
async def reject_text_endpoint(request: RejectRequest):
    """
    Reject text and provide feedback.
    
    - **text**: Text to reject
    - **reason**: Reason for rejection
    - **category**: Optional rejection category
    
    Returns rejection details and suggestions.
    """
    return await controller.reject_text(request)

@router.post("/rewrite-and-evaluate", response_model=TextRewriteResponse)
async def rewrite_and_evaluate_endpoint(request: TextRewriteRequest):
    """
    Rewrite text using brand signature and evaluate the result in one step.
    
    - **brand_id**: Brand identifier
    - **text**: Original text to rewrite and evaluate
    
    Returns the rewritten text and evaluation results.
    """
    return await controller.rewrite_and_evaluate_text(request)

