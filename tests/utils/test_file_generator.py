"""
Utility script to generate test files for RAG testing.

This script creates various test files (text, JSON, image, etc.) 
used in the RAG functionality tests.
"""
import os
import sys
import json
import base64
from pathlib import Path


def create_test_files(output_dir):
    """Create test files for RAG testing.
    
    Args:
        output_dir (str): Directory to write test files to
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Create a simple text file
    with open(os.path.join(output_dir, "sample.txt"), "w") as f:
        f.write("This is a sample text file for testing RAG functionality.\n"
                "It contains multiple lines of text.\n"
                "The agents should be able to process this file correctly.")
    
    # Create a JSON file
    data = {
        "name": "Test Document",
        "properties": {
            "author": "Test Framework",
            "version": 1.0,
            "tags": ["test", "rag", "document"]
        },
        "content": {
            "sections": [
                {"title": "Introduction", "body": "This is a test JSON file."},
                {"title": "Section 1", "body": "This section covers important content."},
                {"title": "Section 2", "body": "This section provides examples."}
            ]
        }
    }
    with open(os.path.join(output_dir, "data.json"), "w") as f:
        json.dump(data, f, indent=2)
    
    # Create a very large text file (approximately 400KB)
    with open(os.path.join(output_dir, "large_document.txt"), "w") as f:
        # Generate a large amount of Lorem Ipsum text
        lorem_ipsum = (
            "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor "
            "incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud "
            "exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure "
            "dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. "
            "Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt "
            "mollit anim id est laborum.\n\n"
        )
        
        # Write the Lorem Ipsum text multiple times to create a large file
        # This will create a file with approximately 400KB of text (about 100K tokens)
        for i in range(800):  # 800 * ~500 bytes = ~400KB
            f.write(f"Section {i+1}:\n\n")
            f.write(lorem_ipsum)
    
    # Create a minimal valid PNG file (1x1 pixel)
    # This is a minimal valid PNG file for a 1x1 transparent pixel
    png_data = base64.b64decode(
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+P+/HgAFEwJgGmBKJQAA"
        "AABJRU5ErkJggg=="
    )
    with open(os.path.join(output_dir, "sample.png"), "wb") as f:
        f.write(png_data)
    
    # Create a file with an unsupported extension
    with open(os.path.join(output_dir, "unsupported.xyz"), "w") as f:
        f.write("This file has an unsupported extension.\n"
                "The RAG system should reject it with a helpful error message.")
    
    print(f"Test files created in {output_dir}")


if __name__ == "__main__":
    # Default output directory is tests/data
    base_dir = Path(__file__).resolve().parent.parent
    default_output_dir = os.path.join(base_dir, "data")
    
    # Allow overriding the output directory
    output_dir = sys.argv[1] if len(sys.argv) > 1 else default_output_dir
    
    create_test_files(output_dir) 