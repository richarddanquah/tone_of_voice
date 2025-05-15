from services.tone_service import process_word_document, analyze_tone, rewrite_with_signature, evaluate_tone
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def main():
    # Process the press releases document
    print("Processing Press Releases document...")
    vectorstore = process_word_document("Press Releases Examples.docx")
    
    # Get all documents from the vectorstore
    documents = vectorstore.get()
    
    # Combine all texts for analysis
    combined_text = " ".join([doc.page_content for doc in documents])
    
    # Analyze the tone
    print("\nAnalyzing tone of voice...")
    signature = analyze_tone(combined_text)
    print("\nBrand Voice Signature:")
    print(signature)
    
    # Example of rewriting a new text with the signature
    example_text = """
    We are excited to announce our new product launch. This innovative solution will help businesses streamline their operations and increase efficiency.
    """
    
    print("\nExample of rewriting text with the brand voice:")
    print("\nOriginal text:")
    print(example_text)
    
    rewritten = rewrite_with_signature(example_text, signature)
    print("\nRewritten text:")
    print(rewritten)
    
    # Evaluate the rewritten text
    print("\nEvaluating the rewritten text...")
    evaluation = evaluate_tone(example_text, rewritten, signature)
    print("\nEvaluation:")
    print(evaluation)

if __name__ == "__main__":
    main() 