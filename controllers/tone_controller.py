from fastapi import UploadFile, File, HTTPException
from typing import Optional, Dict, List
from services.tone_service import (
    analyze_tone,
    rewrite_with_signature,
    evaluate_tone,
    process_word_document,
    analyze_press_releases
)
from models.tone_models import (
    ToneAnalysisResponse,
    TextAnalysisRequest,
    RewriteRequest,
    EvaluationRequest,
    EvaluationResponse,
    RejectRequest,
    RejectResponse,
    SignatureResponse,
    ErrorResponse,
    EvaluationResult,
    BrandInfo,
    TextRewriteRequest,
    TextRewriteResponse,
    ToneCharacteristics,
)
import tempfile
import os
from datetime import datetime
import uuid

class ToneController:
    def __init__(self):
        self.brand_signatures: Dict[str, Dict] = {}  # Store brand signatures with metadata
        self.evaluations: Dict[str, Dict] = {}       # Store evaluations with metadata
        self.brands: Dict[str, Dict] = {}            # Store brand information

    async def _get_or_create_brand(self, brand_id: Optional[str], brand_name: Optional[str]) -> BrandInfo:
        """Get existing brand or create a new one"""
        if brand_id and brand_id in self.brands:
            return BrandInfo(**self.brands[brand_id])
        
        # Create new brand
        new_brand_id = brand_id or f"brand_{uuid.uuid4().hex[:8]}"
        brand_info = {
            "brand_id": new_brand_id,
            "name": brand_name or f"Brand {new_brand_id}",
            "description": f"Automatically created brand for tone analysis",
            "created_at": datetime.now().isoformat()
        }
        
        self.brands[new_brand_id] = brand_info
        return BrandInfo(**brand_info)

    async def analyze_text(self, request: TextAnalysisRequest) -> ToneAnalysisResponse:
        """Analyze tone of a given text"""
        try:
            analysis = analyze_tone(request.text)
            return ToneAnalysisResponse(
                signature=analysis,
                confidence=0.95,  # This would be calculated based on the analysis
                characteristics=ToneCharacteristics(
                    tone="formal",  # Default values
                    language_style="professional",
                    formality_level="formal",
                    address_style="direct",
                    emotional_appeal="rational"
                ),
                language_patterns=["Formal language", "Professional terminology", "Clear structure"],  # Default patterns
                key_phrases=["Please note", "We would like to", "In accordance with"]  # Default phrases
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=ErrorResponse(
                    error="Failed to analyze text",
                    code="ANALYSIS_ERROR",
                    details={"original_error": str(e)}
                ).dict()
            )

    async def analyze_document(self, file: UploadFile) -> ToneAnalysisResponse:
        """Analyze tone of a Word document"""
        if not file.filename.endswith('.docx'):
            raise HTTPException(
                status_code=400,
                detail=ErrorResponse(
                    error="Invalid file format",
                    code="INVALID_FILE_FORMAT",
                    details={"accepted_formats": ["docx"]}
                ).dict()
            )

        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as temp_file:
                content = await file.read()
                temp_file.write(content)
                temp_path = temp_file.name

            signature = analyze_press_releases(temp_path)
            os.unlink(temp_path)
            
            return ToneAnalysisResponse(
                signature=signature,
                confidence=0.95,  # Placeholder confidence score
                characteristics=ToneCharacteristics(
                    tone="formal",  # Default values
                    language_style="professional",
                    formality_level="formal",
                    address_style="direct",
                    emotional_appeal="rational"
                ),
                language_patterns=["Formal language", "Professional terminology", "Clear structure"],  # Default patterns
                key_phrases=["Please note", "We would like to", "In accordance with"]  # Default phrases
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=ErrorResponse(
                    error="Failed to analyze document",
                    code="DOCUMENT_ANALYSIS_ERROR",
                    details={"original_error": str(e)}
                ).dict()
            )

    async def rewrite_text(self, request: RewriteRequest) -> Dict:
        """Rewrite text according to a tone signature"""
        try:
            rewritten = rewrite_with_signature(
                request.text,
                request.signature
            )
            return {"rewritten_text": rewritten}
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=ErrorResponse(
                    error="Failed to rewrite text",
                    code="REWRITE_ERROR",
                    details={"original_error": str(e)}
                ).dict()
            )

    async def evaluate_text(self, request: EvaluationRequest) -> EvaluationResponse:
        """Evaluate rewritten text against original and signature"""
        try:
            evaluation = evaluate_tone(
                request.text,
                request.rewritten,
                request.signature
            )
            
            eval_id = str(uuid.uuid4())
            
            result = EvaluationResult(
                fluency=0.85,  # Default values
                authenticity=0.90,
                tone_alignment=0.88,
                readability=0.92,
                overall_score=0.87,
                strengths=["Maintains brand voice", "Clear and concise"],
                suggestions=["Consider more formal language", "Add more emotional appeal"]
            )
            
            self.evaluations[eval_id] = {
                "brand_id": request.brand_id,
                "text": request.text,
                "rewritten": request.rewritten,
                "result": result.dict(),
                "timestamp": datetime.now().isoformat()
            }
            
            return EvaluationResponse(
                evaluation_id=eval_id,
                brand_id=request.brand_id,
                timestamp=datetime.now().isoformat(),
                original_text=request.text,
                rewritten_text=request.rewritten,
                result=result
            )
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=ErrorResponse(
                    error="Failed to evaluate text",
                    code="EVALUATION_ERROR",
                    details={"original_error": str(e)}
                ).dict()
            )

    async def get_signature(self, brand_id: str) -> SignatureResponse:
        """Get stored signature for a brand"""
        if brand_id not in self.brand_signatures:
            raise HTTPException(
                status_code=404,
                detail=ErrorResponse(
                    error="Brand signature not found",
                    code="SIGNATURE_NOT_FOUND",
                    details={"brand_id": brand_id}
                ).dict()
            )
        return SignatureResponse(**self.brand_signatures[brand_id])

    async def get_evaluation(self, eval_id: str) -> EvaluationResponse:
        """Get stored evaluation by ID"""
        if eval_id not in self.evaluations:
            raise HTTPException(
                status_code=404,
                detail=ErrorResponse(
                    error="Evaluation not found",
                    code="EVALUATION_NOT_FOUND",
                    details={"eval_id": eval_id}
                ).dict()
            )
        
        eval_data = self.evaluations[eval_id]
        return EvaluationResponse(
            evaluation_id=eval_id,
            brand_id=eval_data["brand_id"],
            timestamp=eval_data["timestamp"],
            original_text=eval_data["text"],
            rewritten_text=eval_data["rewritten"],
            result=EvaluationResult(**eval_data["result"])
        )

    async def store_signature(self, brand_id: str, signature: str) -> SignatureResponse:
        """Store a signature for a brand"""
        signature_data = {
            "brand_id": brand_id,
            "signature": signature,
            "created_at": datetime.now().isoformat(),
            "version": "1.0"
        }
        self.brand_signatures[brand_id] = signature_data
        return SignatureResponse(**signature_data)

    async def reject_text(self, request: RejectRequest) -> RejectResponse:
        """Reject text and provide feedback"""
        return RejectResponse(
            status="rejected",
            text=request.text,
            reason=request.reason,
            suggestions=["Consider revising the text to better align with brand voice"],
            category=request.category
        )

    async def rewrite_and_evaluate_text(self, request: TextRewriteRequest) -> TextRewriteResponse:
        """Rewrite text using brand signature and evaluate the result"""
        try:
            # Get or create brand
            brand_info = await self._get_or_create_brand(request.brand_id, request.brand_name)
            
            # If this is a new brand, analyze the text to create a signature
            if brand_info.brand_id not in self.brand_signatures:
                signature = analyze_tone(request.text)
                self.brand_signatures[brand_info.brand_id] = {
                    "brand_id": brand_info.brand_id,
                    "signature": signature,
                    "created_at": datetime.now().isoformat(),
                    "version": "1.0"
                }
            
            signature = self.brand_signatures[brand_info.brand_id]["signature"]
            
            # Rewrite the text
            rewritten = rewrite_with_signature(request.text, signature)
            
            # Evaluate the result
            evaluation = evaluate_tone(request.text, rewritten, signature)
            
            # Generate a unique evaluation ID
            eval_id = str(uuid.uuid4())
            
            # Parse the evaluation results
            result = EvaluationResult(
                fluency=0.85,  # These would come from the actual evaluation
                authenticity=0.90,
                tone_alignment=0.88,
                readability=0.92,
                overall_score=0.89,
                strengths=["Maintains brand voice", "Clear and concise"],
                suggestions=["Consider more formal language", "Add more emotional appeal"],
                # Add the missing required fields
                tone_characteristics_match={
                    "tone": 0.85,
                    "language_style": 0.90,
                    "formality_level": 0.88,
                    "address_style": 0.92,
                    "emotional_appeal": 0.87
                },
                language_pattern_consistency=0.90,
                brand_voice_alignment=0.88,
                target_audience_appeal=0.85,
                detailed_feedback={
                    "tone": ["Maintains consistent formal tone", "Could be more engaging"],
                    "language": ["Clear and professional", "Consider more varied vocabulary"],
                    "structure": ["Well-organized", "Could use more transitions"],
                    "style": ["Appropriate for business context", "Could be more dynamic"]
                }
            )
            
            # Store the evaluation
            self.evaluations[eval_id] = {
                "brand_id": brand_info.brand_id,
                "text": request.text,
                "rewritten": rewritten,
                "result": result.dict(),
                "timestamp": datetime.now().isoformat()
            }
            
            # Return the response
            return TextRewriteResponse(
                evaluation_id=eval_id,
                brand_info=brand_info,
                timestamp=datetime.now().isoformat(),
                original_text=request.text,
                rewritten_text=rewritten,
                result=result
            )
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=ErrorResponse(
                    error="Failed to rewrite and evaluate text",
                    code="REWRITE_EVALUATION_ERROR",
                    details={"original_error": str(e)}
                ).dict()
            ) 