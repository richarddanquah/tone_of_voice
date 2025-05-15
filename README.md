# Tone of Voice Analysis and Rewriting Service

A FastAPI-based service that analyzes, rewrites, and evaluates text based on tone characteristics. This service helps maintain consistent brand voice across different types of content by overcoming the generic and impersonal nature of AI-generated text.

## Core Tone Characteristics

The service analyzes and maintains five key characteristics of brand voice:

1. **Tone**
   - Formal vs. Casual
   - Professional vs. Friendly
   - Authoritative vs. Collaborative
   - Warm vs. Direct

2. **Language Style**
   - Technical vs. Conversational
   - Academic vs. Creative
   - Professional vs. Informal
   - Complex vs. Simple

3. **Formality Level**
   - Formal
   - Semi-formal
   - Informal
   - Technical

4. **Address Style**
   - Direct vs. Indirect
   - Personal vs. Impersonal
   - Collective vs. Individual
   - Hierarchical vs. Egalitarian

5. **Emotional Appeal**
   - Rational vs. Emotional
   - Inspirational vs. Informative
   - Humorous vs. Serious
   - Authoritative vs. Approachable

## NLP Analysis Capabilities

The service employs advanced NLP techniques to analyze and maintain brand voice:

1. **Semantic Analysis**
   - Word choice patterns
   - Phrase structures
   - Contextual meaning
   - Cultural nuances

2. **Syntactic Analysis**
   - Sentence structure
   - Grammar patterns
   - Punctuation usage
   - Paragraph organization

3. **Pattern Recognition**
   - Recurring phrases
   - Common expressions
   - Brand-specific terminology
   - Communication patterns

4. **Sentiment Analysis**
   - Emotional undertones
   - Tone consistency
   - Brand voice alignment
   - Audience engagement

## Features

### 1. Text Analysis
- Analyze the tone of any text input
- Extract tone characteristics:
  - Overall tone (formal, casual, friendly, etc.)
  - Language style (technical, conversational, academic, etc.)
  - Formality level
  - Address style
  - Emotional appeal
- Identify language patterns and key phrases
- Provide confidence scores for analysis

### 2. Document Analysis
- Process Word documents (.docx files)
- Extract and analyze text from both paragraphs and tables
- Generate comprehensive tone signatures
- Maintain document structure while analyzing content

### 3. Text Rewriting
- Rewrite text to match specific tone signatures
- Preserve key information and keywords
- Maintain original meaning while adjusting tone
- Support for multiple tone styles

### 4. Evaluation
- Evaluate rewritten text against original content
- Provide detailed metrics:
  - Fluency
  - Authenticity
  - Tone alignment
  - Readability
  - Overall score
- Generate strengths and improvement suggestions
- Track brand voice alignment
- Assess target audience appeal

### 5. Brand Voice Management
- Store and retrieve brand signatures
- Track multiple brand voices
- Maintain version history of tone signatures
- Support for brand-specific evaluations

## API Endpoints

### Text Analysis
```http
POST /tone/analyze/text
```
Analyze the tone of a given text.

### Document Analysis
```http
POST /tone/analyze/document
```
Analyze the tone of a Word document.

### Text Rewriting
```http
POST /tone/rewrite
```
Rewrite text according to a tone signature.

### Evaluation
```http
POST /tone/evaluate
```
Evaluate rewritten text against original and signature.

### Brand Signature Management
```http
GET /tone/signature/{brand_id}
POST /tone/signature/{brand_id}
```
Get or store brand signatures.

### Combined Operations
```http
POST /tone/rewrite-and-evaluate
```
Rewrite text using brand signature and evaluate the result in one step.

## Installation

1. Clone the repository:
```bash
git clone [repository-url]
cd tone_of_voice
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your OpenAI API key
```

## Usage

1. Start the server:
```bash
uvicorn main:app --reload
```

2. Access the API documentation:
```
http://localhost:8000/docs
```

### Example Request

```python
import requests

# Analyze text
response = requests.post(
    "http://localhost:8000/tone/analyze/text",
    json={
        "text": "Your text to analyze",
        "language": "en"
    }
)
print(response.json())

# Rewrite text
response = requests.post(
    "http://localhost:8000/tone/rewrite",
    json={
        "text": "Text to rewrite",
        "signature": "formal,professional",
        "preserve_keywords": ["important", "terms"]
    }
)
print(response.json())

# Analyze document
with open('document.docx', 'rb') as f:
    files = {'file': ('document.docx', f, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')}
    response = requests.post(
        "http://localhost:8000/tone/analyze/document",
        files=files
    )
print(response.json())

# Rewrite and evaluate text
response = requests.post(
    "http://localhost:8000/tone/rewrite-and-evaluate",
    json={
        "text": "Original text to rewrite",
        "brand_id": "brand123",
        "brand_name": "Example Brand"
    }
)
print(response.json())
```

## Error Handling

The API uses standard HTTP status codes and returns detailed error messages in the following format:

```json
{
    "error": "Error description",
    "code": "ERROR_CODE",
    "details": {
        "additional_info": "More specific error details"
    }
}
```

Common error scenarios:

1. **Invalid File Format (400)**
   - Occurs when uploading non-docx files
   - Solution: Ensure file is in .docx format

2. **Analysis Error (500)**
   - Occurs during text analysis
   - Solution: Check text length and content validity

3. **Document Analysis Error (500)**
   - Occurs during document processing
   - Solution: Verify document structure and content

4. **Rewrite Error (500)**
   - Occurs during text rewriting
   - Solution: Check signature format and text content

5. **Evaluation Error (500)**
   - Occurs during text evaluation
   - Solution: Ensure all required fields are provided

6. **Signature Not Found (404)**
   - Occurs when accessing non-existent brand signatures
   - Solution: Create brand signature first

## Rate Limiting

The API implements rate limiting to ensure fair usage:
- 100 requests per minute per IP
- 1000 requests per hour per API key

## Best Practices

1. **Text Analysis**
   - Keep text length under 5000 characters for optimal performance
   - Use clear, well-structured text for better analysis

2. **Document Processing**
   - Ensure documents are properly formatted
   - Maximum file size: 10MB
   - Supported formats: .docx only

3. **Brand Signatures**
   - Create unique signatures for different content types
   - Update signatures periodically to maintain accuracy
   - Store signature IDs for future reference

4. **Error Handling**
   - Implement proper error handling in your application
   - Use appropriate HTTP status codes
   - Log errors for debugging

## Dependencies

- FastAPI: Web framework
- LangChain: LLM integration and prompt management
- OpenAI: Advanced language model for tone analysis
- Python-docx: Document processing
- Pydantic: Data validation
- ChromaDB: Vector storage for pattern matching
- Redis: Caching
- spaCy: NLP processing
- NLTK: Additional NLP capabilities
- Sentence Transformers: Semantic similarity analysis

## Project Structure

```
tone_of_voice/
├── controllers/         # Request handlers
├── models/             # Data models
├── routes/             # API routes
├── services/           # Business logic
├── chroma_db/          # Vector database
├── main.py            # Application entry
└── requirements.txt    # Dependencies
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

[Your License]

## Contact

[Your Contact Information]
