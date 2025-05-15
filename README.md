# Tone of Voice Analysis and Rewriting Service

A FastAPI-based service that uses LangChain and ChromaDB to analyze, rewrite, and evaluate text based on tone characteristics. This service helps maintain consistent brand voice across different types of content.

## Architecture

### 1. Tone Controller (`controllers/tone_controller.py`)
Handles HTTP requests and responses:
- Text analysis endpoints
- Document processing
- Text rewriting
- Evaluation endpoints
- Brand signature management

### 2. Tone Service (`services/tone_service.py`)
Core business logic implementation:
- LLM integration using LangChain
- Text analysis using OpenAI
- Document processing with python-docx
- Vector storage with ChromaDB
- Text rewriting and evaluation

### 3. Tone Routes (`routes/tone_routes.py`)
API route definitions:
- POST `/tone/analyze/text`
- POST `/tone/analyze/document`
- POST `/tone/rewrite`
- POST `/tone/evaluate`
- POST `/tone/rewrite-and-evaluate`
- GET/POST `/tone/signature/{brand_id}`

## Key Components

### LangChain Integration
```python
from langchain.chains import LLMChain
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate

# Example from tone_service.py
def analyze_tone(text: str):
    chain = LLMChain(llm=OpenAI(temperature=0), prompt=signature_prompt)
    return chain.run({"text": text})
```

### ChromaDB Vector Store
```python
from langchain.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings

# Example from tone_service.py
def process_document(file_path: str):
    embeddings = OpenAIEmbeddings()
    vectorstore = Chroma.from_documents(
        documents=texts,
        embedding=embeddings,
        persist_directory="./chroma_db"
    )
```

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
# Add your OpenAI API key to .env
OPENAI_API_KEY=your_api_key_here
```

## Running the Application

1. Start the FastAPI server:
```bash
uvicorn main:app --reload
```

2. Access the API documentation:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## API Usage Examples

### 1. Analyze Text
```python
import requests

response = requests.post(
    "http://localhost:8000/tone/analyze/text",
    json={
        "text": "Your text to analyze"
    }
)
print(response.json())
```

### 2. Process Document
```python
with open('document.docx', 'rb') as f:
    files = {'file': ('document.docx', f, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')}
    response = requests.post(
        "http://localhost:8000/tone/analyze/document",
        files=files
    )
print(response.json())
```

### 3. Rewrite Text
```python
response = requests.post(
    "http://localhost:8000/tone/rewrite",
    json={
        "text": "Text to rewrite",
        "signature": "formal,professional"
    }
)
print(response.json())
```

## Project Structure
```
tone_of_voice/
├── controllers/
│   └── tone_controller.py    # Request handling
├── services/
│   ├── tone_service.py      # Core business logic
├── routes/
│   └── tone_routes.py       # API route definitions
├── models/
│   └── tone_models.py       # Pydantic models
├── chroma_db/               # Vector database storage
├── main.py                 # FastAPI application
└── requirements.txt        # Dependencies
```

## Dependencies
- FastAPI: Web framework
- LangChain: LLM integration
- OpenAI: Language model
- ChromaDB: Vector database
- python-docx: Document processing
- Pydantic: Data validation

## Error Handling
The API returns standardized error responses:
```json
{
    "error": "Error description",
    "code": "ERROR_CODE",
    "details": {
        "additional_info": "More specific error details"
    }
}
```

## Contributing
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request
