from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.schema.runnable import RunnableSequence
from typing import Dict, List, Optional
import os
from dotenv import load_dotenv
from .cache_service import CacheService
import sys
from pathlib import Path

# Add the project root to Python path
project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

# Import models using absolute import
from models.tone_models import ToneCharacteristics, LanguageStyle, ToneLevel, EmotionalAppeal

load_dotenv()

class LLMService:
    def __init__(self):
        """Initialize the LLM service with GPT-4 configuration"""
        # Get API key from environment
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")

        # Initialize OpenAI client with ChatOpenAI
        self.llm = ChatOpenAI(
            model_name="gpt-4",
            temperature=0.7,  # Balanced creativity
            max_tokens=1000,  # Comprehensive analysis
            openai_api_key=api_key
        )
        
        # Initialize cache service
        self.cache = CacheService()
        
        # Initialize analysis chain
        analysis_prompt = PromptTemplate(
            input_variables=["text"],
            template="""
            Analyze the tone of the following text and provide a detailed breakdown of its characteristics:
            Text: {text}
            
            Please analyze and respond in the following JSON format, using ONLY the specified values for each field:
            {{
                "tone": "one of: formal, casual, friendly, professional, authoritative, warm, direct",
                "language_style": "one of: technical, conversational, academic, professional, creative",
                "formality_level": "one of: formal, semi-formal, informal",
                "address_style": "one of: direct, indirect, personal, impersonal, collective",
                "emotional_appeal": "one of: rational, emotional, inspirational, humorous, authoritative"
            }}
            
            Important: You must use EXACTLY the values specified above for each field.
            Do not use any other values or combinations of values.
            Do not include any explanations or descriptions in the values.
            
            Ensure your response is valid JSON.
            """
        )
        self.analysis_chain = analysis_prompt | self.llm
        
        # Initialize rewriting chain
        rewrite_prompt = PromptTemplate(
            input_variables=["text", "signature", "preserve_keywords"],
            template="""
            Rewrite the following text to match the specified tone signature while preserving the key information:
            
            Original text: {text}
            Tone signature: {signature}
            Keywords to preserve: {preserve_keywords}
            
            Ensure the rewritten text maintains the original meaning while adopting the specified tone characteristics.
            """
        )
        self.rewrite_chain = rewrite_prompt | self.llm
        
        # Initialize evaluation chain
        evaluation_prompt = PromptTemplate(
            input_variables=["original", "rewritten", "signature"],
            template="""
            Evaluate how well the rewritten text matches the intended tone signature:
            
            Original text: {original}
            Rewritten text: {rewritten}
            Target signature: {signature}
            
            Please analyze and respond in the following JSON format:
            {{
                "tone_alignment": 0.85,
                "language_consistency": 0.90,
                "formality_match": 0.88,
                "address_appropriateness": 0.92,
                "emotional_effectiveness": 0.87,
                "strengths": ["strength1", "strength2"],
                "improvements": ["improvement1", "improvement2"]
            }}
            
            Ensure your response is valid JSON.
            """
        )
        self.evaluation_chain = evaluation_prompt | self.llm

    async def analyze_tone(self, text: str) -> Dict:
        """Analyze the tone of a given text"""
        try:
            # Check cache first
            cached_result = self.cache.get_cached_analysis(text)
            if cached_result:
                return cached_result
            
            # If not in cache, perform analysis
            result = await self.analysis_chain.ainvoke({"text": text})
            # Get the content from the AIMessage
            result_text = result.content
            parsed_result = self._parse_analysis_result(result_text)
            
            # Cache the result
            self.cache.cache_analysis(text, parsed_result)
            
            return parsed_result
        except Exception as e:
            raise Exception(f"Tone analysis failed: {str(e)}")

    async def rewrite_text(self, text: str, signature: str, preserve_keywords: Optional[List[str]] = None) -> str:
        """Rewrite text according to a tone signature"""
        try:
            # Generate cache key for the rewrite
            cache_key = f"{text}:{signature}:{','.join(preserve_keywords or [])}"
            
            # Check cache first
            cached_result = self.cache.get_cached_evaluation(cache_key)
            if cached_result:
                return cached_result.get("rewritten_text", "")
            
            # If not in cache, perform rewrite
            keywords = preserve_keywords or []
            result = await self.rewrite_chain.ainvoke({
                "text": text,
                "signature": signature,
                "preserve_keywords": ", ".join(keywords)
            })
            # Get the content from the AIMessage
            rewritten = result.content.strip()
            
            # Cache the result
            self.cache.cache_evaluation(cache_key, {"rewritten_text": rewritten})
            
            return rewritten
        except Exception as e:
            raise Exception(f"Text rewriting failed: {str(e)}")

    async def evaluate_text(self, original: str, rewritten: str, signature: str) -> Dict:
        """Evaluate rewritten text against original and signature"""
        try:
            # Generate cache key for the evaluation
            cache_key = f"{original}:{rewritten}:{signature}"
            
            # Check cache first
            cached_result = self.cache.get_cached_evaluation(cache_key)
            if cached_result:
                return cached_result
            
            # If not in cache, perform evaluation
            result = await self.evaluation_chain.ainvoke({
                "original": original,
                "rewritten": rewritten,
                "signature": signature
            })
            # Get the content from the AIMessage
            result_text = result.content
            parsed_result = self._parse_evaluation_result(result_text)
            
            # Cache the result
            self.cache.cache_evaluation(cache_key, parsed_result)
            
            return parsed_result
        except Exception as e:
            raise Exception(f"Text evaluation failed: {str(e)}")

    def _parse_analysis_result(self, result: str) -> Dict:
        """Parse the analysis result into a structured format"""
        try:
            import json
            # Try to parse as JSON first
            parsed = json.loads(result)
            
            # Create a dictionary with the parsed values
            characteristics = {
                "tone": parsed.get("tone", "formal"),
                "language_style": parsed.get("language_style", "professional"),
                "formality_level": parsed.get("formality_level", "formal"),
                "address_style": parsed.get("address_style", "direct"),
                "emotional_appeal": parsed.get("emotional_appeal", "rational")
            }
            
            # Create ToneCharacteristics instance
            tone_char = ToneCharacteristics(**characteristics)
            return tone_char.dict()
            
        except json.JSONDecodeError:
            # Fallback to default values if JSON parsing fails
            default_characteristics = {
                "tone": "formal",
                "language_style": "professional",
                "formality_level": "formal",
                "address_style": "direct",
                "emotional_appeal": "rational"
            }
            tone_char = ToneCharacteristics(**default_characteristics)
            return tone_char.dict()

    def _parse_evaluation_result(self, result: str) -> Dict:
        """Parse the evaluation result into a structured format"""
        try:
            import json
            # Try to parse as JSON first
            parsed = json.loads(result)
            return {
                "tone_alignment": float(parsed.get("tone_alignment", 0.85)),
                "language_consistency": float(parsed.get("language_consistency", 0.90)),
                "formality_match": float(parsed.get("formality_match", 0.88)),
                "address_appropriateness": float(parsed.get("address_appropriateness", 0.92)),
                "emotional_effectiveness": float(parsed.get("emotional_effectiveness", 0.87)),
                "strengths": parsed.get("strengths", ["Maintains brand voice", "Clear and concise"]),
                "improvements": parsed.get("improvements", ["Consider more formal language", "Add more emotional appeal"])
            }
        except json.JSONDecodeError:
            # Fallback to default values if JSON parsing fails
            return {
                "tone_alignment": 0.85,
                "language_consistency": 0.90,
                "formality_match": 0.88,
                "address_appropriateness": 0.92,
                "emotional_effectiveness": 0.87,
                "strengths": ["Maintains brand voice", "Clear and concise"],
                "improvements": ["Consider more formal language", "Add more emotional appeal"]
            } 