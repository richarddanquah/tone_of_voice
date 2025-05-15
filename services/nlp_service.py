import spacy
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Tuple
import numpy as np
from collections import Counter
import re

# Download required NLTK data
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('averaged_perceptron_tagger')

class NLPService:
    def __init__(self):
        """Initialize NLP components"""
        # Load spaCy model
        self.nlp = spacy.load("en_core_web_sm")
        
        # Initialize NLTK components
        self.stop_words = set(stopwords.words('english'))
        self.lemmatizer = WordNetLemmatizer()
        
        # Initialize Sentence Transformer
        self.sentence_transformer = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Initialize pattern recognition
        self.patterns = {
            'formal': [
                r'\b(please|kindly|would you|could you)\b',
                r'\b(regarding|concerning|with respect to)\b',
                r'\b(accordingly|therefore|thus|hence)\b'
            ],
            'casual': [
                r'\b(hey|hi|hello|thanks|cheers)\b',
                r'\b(great|awesome|cool|nice)\b',
                r'\b(just|actually|basically|literally)\b'
            ],
            'professional': [
                r'\b(implement|develop|create|establish)\b',
                r'\b(strategy|solution|approach|methodology)\b',
                r'\b(optimize|enhance|improve|streamline)\b'
            ]
        }

    def analyze_text(self, text: str) -> Dict:
        """Perform comprehensive text analysis"""
        # Basic text statistics
        stats = self._get_text_statistics(text)
        
        # Linguistic features
        linguistic = self._analyze_linguistic_features(text)
        
        # Pattern recognition
        patterns = self._recognize_patterns(text)
        
        # Semantic analysis
        semantic = self._analyze_semantics(text)
        
        return {
            "statistics": stats,
            "linguistic_features": linguistic,
            "patterns": patterns,
            "semantic_analysis": semantic
        }

    def _get_text_statistics(self, text: str) -> Dict:
        """Calculate basic text statistics"""
        sentences = sent_tokenize(text)
        words = word_tokenize(text)
        
        return {
            "sentence_count": len(sentences),
            "word_count": len(words),
            "unique_words": len(set(words)),
            "avg_sentence_length": len(words) / len(sentences) if sentences else 0,
            "stop_word_ratio": len([w for w in words if w.lower() in self.stop_words]) / len(words) if words else 0
        }

    def _analyze_linguistic_features(self, text: str) -> Dict:
        """Analyze linguistic features using spaCy"""
        doc = self.nlp(text)
        
        # Part of speech analysis
        pos_counts = Counter([token.pos_ for token in doc])
        
        # Named entity recognition
        entities = [(ent.text, ent.label_) for ent in doc.ents]
        
        # Dependency analysis
        dependencies = [(token.text, token.dep_) for token in doc]
        
        return {
            "pos_distribution": dict(pos_counts),
            "entities": entities,
            "dependencies": dependencies,
            "noun_phrases": [chunk.text for chunk in doc.noun_chunks]
        }

    def _recognize_patterns(self, text: str) -> Dict:
        """Recognize patterns in text"""
        pattern_matches = {}
        
        for tone, patterns in self.patterns.items():
            matches = []
            for pattern in patterns:
                found = re.findall(pattern, text, re.IGNORECASE)
                if found:
                    matches.extend(found)
            pattern_matches[tone] = list(set(matches))
        
        return pattern_matches

    def _analyze_semantics(self, text: str) -> Dict:
        """Perform semantic analysis using Sentence Transformers"""
        # Get sentence embeddings
        sentences = sent_tokenize(text)
        embeddings = self.sentence_transformer.encode(sentences)
        
        # Calculate semantic similarity between sentences
        similarity_matrix = np.zeros((len(sentences), len(sentences)))
        for i in range(len(sentences)):
            for j in range(len(sentences)):
                similarity_matrix[i][j] = np.dot(embeddings[i], embeddings[j]) / (
                    np.linalg.norm(embeddings[i]) * np.linalg.norm(embeddings[j])
                )
        
        # Extract key phrases using embeddings
        key_phrases = self._extract_key_phrases(text, embeddings)
        
        return {
            "sentence_similarity": similarity_matrix.tolist(),
            "key_phrases": key_phrases,
            "semantic_coherence": float(np.mean(similarity_matrix))
        }

    def _extract_key_phrases(self, text: str, embeddings: np.ndarray) -> List[str]:
        """Extract key phrases using semantic similarity"""
        doc = self.nlp(text)
        phrases = []
        
        # Extract noun phrases
        for chunk in doc.noun_chunks:
            if len(chunk.text.split()) > 1:  # Only multi-word phrases
                phrases.append(chunk.text)
        
        # Calculate phrase importance based on embedding similarity
        if phrases:
            phrase_embeddings = self.sentence_transformer.encode(phrases)
            importance_scores = []
            
            for phrase_emb in phrase_embeddings:
                # Calculate average similarity to all sentences
                similarities = [
                    np.dot(phrase_emb, sent_emb) / (
                        np.linalg.norm(phrase_emb) * np.linalg.norm(sent_emb)
                    )
                    for sent_emb in embeddings
                ]
                importance_scores.append(np.mean(similarities))
            
            # Return top phrases by importance
            top_indices = np.argsort(importance_scores)[-5:]  # Top 5 phrases
            return [phrases[i] for i in top_indices]
        
        return []

    def get_tone_characteristics(self, text: str) -> Dict:
        """Extract tone characteristics from text"""
        doc = self.nlp(text)
        patterns = self._recognize_patterns(text)
        
        # Analyze formality
        formality_score = self._calculate_formality(doc, patterns)
        
        # Analyze emotional appeal
        emotional_score = self._analyze_emotional_appeal(doc)
        
        # Analyze language style
        style_score = self._analyze_language_style(doc, patterns)
        
        return {
            "formality_level": formality_score,
            "emotional_appeal": emotional_score,
            "language_style": style_score,
            "detected_patterns": patterns
        }

    def _calculate_formality(self, doc, patterns: Dict) -> str:
        """Calculate formality level"""
        formal_markers = len(patterns.get('formal', []))
        casual_markers = len(patterns.get('casual', []))
        
        if formal_markers > casual_markers * 2:
            return "formal"
        elif casual_markers > formal_markers * 2:
            return "casual"
        else:
            return "semi-formal"

    def _analyze_emotional_appeal(self, doc) -> str:
        """Analyze emotional appeal in text"""
        # This is a simplified version - you might want to use a more sophisticated approach
        emotional_words = {
            'rational': ['because', 'therefore', 'thus', 'consequently'],
            'emotional': ['feel', 'believe', 'hope', 'wish'],
            'inspirational': ['achieve', 'succeed', 'excel', 'inspire'],
            'humorous': ['funny', 'amusing', 'entertaining', 'witty']
        }
        
        word_counts = {category: 0 for category in emotional_words}
        
        for token in doc:
            for category, words in emotional_words.items():
                if token.lemma_.lower() in words:
                    word_counts[category] += 1
        
        return max(word_counts.items(), key=lambda x: x[1])[0]

    def _analyze_language_style(self, doc, patterns: Dict) -> str:
        """Analyze language style"""
        professional_markers = len(patterns.get('professional', []))
        
        if professional_markers > 3:
            return "professional"
        elif any(token.pos_ == "NOUN" and token.is_stop == False for token in doc):
            return "technical"
        else:
            return "conversational" 