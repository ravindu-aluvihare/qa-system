"""
Utility functions for the QA System
"""
import PyPDF2
import docx
from io import BytesIO

def extract_text_from_pdf(file):
    """
    Extract text from PDF file
    
    Args:
        file: Uploaded PDF file object
        
    Returns:
        str: Extracted text from PDF
    """
    try:
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""
        
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        
        return text.strip()
    except Exception as e:
        return f"Error reading PDF: {str(e)}"

def extract_text_from_docx(file):
    """
    Extract text from DOCX file
    
    Args:
        file: Uploaded DOCX file object
        
    Returns:
        str: Extracted text from DOCX
    """
    try:
        doc = docx.Document(file)
        text = ""
        
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        
        return text.strip()
    except Exception as e:
        return f"Error reading DOCX: {str(e)}"

def extract_text_from_txt(file):
    """
    Extract text from TXT file
    
    Args:
        file: Uploaded TXT file object
        
    Returns:
        str: Extracted text from TXT
    """
    try:
        # Read bytes and decode
        text = file.read().decode('utf-8')
        return text.strip()
    except Exception as e:
        return f"Error reading TXT: {str(e)}"

def process_uploaded_file(uploaded_file):
    """
    Process uploaded file based on its type
    
    Args:
        uploaded_file: Streamlit uploaded file object
        
    Returns:
        str: Extracted text from the file
    """
    file_extension = uploaded_file.name.split('.')[-1].lower()
    
    if file_extension == 'pdf':
        return extract_text_from_pdf(uploaded_file)
    elif file_extension == 'docx':
        return extract_text_from_docx(uploaded_file)
    elif file_extension == 'txt':
        return extract_text_from_txt(uploaded_file)
    else:
        return "Unsupported file format. Please upload PDF, DOCX, or TXT files."

def truncate_text(text, max_length=5000):
    """
    Truncate text to maximum length
    
    Args:
        text: Input text
        max_length: Maximum allowed length
        
    Returns:
        str: Truncated text with warning if truncated
    """
    if len(text) > max_length:
        return text[:max_length] + f"\n\n[Text truncated to {max_length} characters]"
    return text