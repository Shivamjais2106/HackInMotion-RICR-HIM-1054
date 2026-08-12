"""
PDF Soil Report Extractor
Extracts soil parameters from PDF reports
"""

import re
import logging

logger = logging.getLogger(__name__)

def extract_soil_values_from_pdf_text(text):
    """
    Extract soil parameters from PDF text using regex patterns
    """
    values = {
        'nitrogen': None,
        'phosphorus': None,
        'potassium': None,
        'ph': None,
        'rainfall': None,
        'temperature': None,
        'humidity': None
    }
    
    try:
        # Pattern matching for different parameter names
        patterns = {
            'nitrogen': [
                r'nitrogen[:\s]+(\d+\.?\d*)',
                r'N[:\s]+(\d+\.?\d*)',
                r'N\s*\([^)]*\)[:\s]+(\d+\.?\d*)',
                r'नाइट्रोजन[:\s]+(\d+\.?\d*)',
            ],
            'phosphorus': [
                r'phosphorus[:\s]+(\d+\.?\d*)',
                r'P[:\s]+(\d+\.?\d*)',
                r'P\s*\([^)]*\)[:\s]+(\d+\.?\d*)',
                r'फॉस्फोरस[:\s]+(\d+\.?\d*)',
            ],
            'potassium': [
                r'potassium[:\s]+(\d+\.?\d*)',
                r'K[:\s]+(\d+\.?\d*)',
                r'K\s*\([^)]*\)[:\s]+(\d+\.?\d*)',
                r'पोटेशियम[:\s]+(\d+\.?\d*)',
            ],
            'ph': [
                r'pH[:\s]+(\d+\.?\d*)',
                r'ph[:\s]+(\d+\.?\d*)',
                r'पीएच[:\s]+(\d+\.?\d*)',
            ],
            'rainfall': [
                r'rainfall[:\s]+(\d+\.?\d*)',
                r'rain[:\s]+(\d+\.?\d*)',
                r'वर्षा[:\s]+(\d+\.?\d*)',
            ],
            'temperature': [
                r'temperature[:\s]+(\d+\.?\d*)',
                r'temp[:\s]+(\d+\.?\d*)',
                r'तापमान[:\s]+(\d+\.?\d*)',
            ],
            'humidity': [
                r'humidity[:\s]+(\d+\.?\d*)',
                r'आर्द्रता[:\s]+(\d+\.?\d*)',
            ]
        }
        
        # Convert text to lowercase for matching
        text_lower = text.lower()
        
        for param, pattern_list in patterns.items():
            for pattern in pattern_list:
                match = re.search(pattern, text_lower, re.IGNORECASE)
                if match:
                    try:
                        values[param] = float(match.group(1))
                        logger.info(f"Extracted {param}: {values[param]}")
                        break
                    except (ValueError, IndexError):
                        continue
        
        return values
    
    except Exception as e:
        logger.error(f"Error extracting soil values from PDF: {e}")
        return values


def extract_text_from_pdf(pdf_file):
    """
    Extract text from PDF file
    Supports both PyPDF2 and pdfplumber
    """
    try:
        # Try using pdfplumber first (better for text extraction)
        try:
            import pdfplumber
            text = ""
            with pdfplumber.open(pdf_file) as pdf:
                for page in pdf.pages:
                    text += page.extract_text() or ""
            return text
        except ImportError:
            # Fallback to PyPDF2
            try:
                from PyPDF2 import PdfReader
                text = ""
                pdf_reader = PdfReader(pdf_file)
                for page in pdf_reader.pages:
                    text += page.extract_text()
                return text
            except ImportError:
                logger.warning("No PDF library available. Install pdfplumber or PyPDF2")
                return ""
    
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {e}")
        return ""


def process_soil_report_pdf(pdf_file):
    """
    Main function to process soil report PDF
    Returns extracted soil parameters
    """
    try:
        # Extract text from PDF
        text = extract_text_from_pdf(pdf_file)
        
        if not text:
            return {
                'success': False,
                'error': 'Could not extract text from PDF',
                'values': {}
            }
        
        # Extract soil values from text
        values = extract_soil_values_from_pdf_text(text)
        
        # Check if any values were extracted
        extracted_count = sum(1 for v in values.values() if v is not None)
        
        if extracted_count == 0:
            return {
                'success': False,
                'error': 'No soil parameters found in PDF',
                'values': values
            }
        
        return {
            'success': True,
            'message': f'Successfully extracted {extracted_count} parameters',
            'values': values,
            'extracted_text': text[:500]  # First 500 chars for debugging
        }
    
    except Exception as e:
        logger.error(f"Error processing soil report PDF: {e}")
        return {
            'success': False,
            'error': str(e),
            'values': {}
        }
