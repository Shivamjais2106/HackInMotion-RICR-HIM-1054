"""
Create a sample soil report PDF for testing
"""
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch

def create_sample_soil_report():
    """Create a sample soil report PDF"""
    filename = "sample_soil_report.pdf"
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter
    
    # Title
    c.setFont("Helvetica-Bold", 16)
    c.drawString(1*inch, height - 1*inch, "SOIL TEST REPORT")
    
    # Farmer Info
    c.setFont("Helvetica", 10)
    c.drawString(1*inch, height - 1.5*inch, "Farmer Name: Rajesh Kumar")
    c.drawString(1*inch, height - 1.7*inch, "Location: Maharashtra, India")
    c.drawString(1*inch, height - 1.9*inch, "Date: 2026-04-17")
    
    # Soil Parameters
    c.setFont("Helvetica-Bold", 12)
    c.drawString(1*inch, height - 2.5*inch, "SOIL PARAMETERS:")
    
    c.setFont("Helvetica", 10)
    y_position = height - 2.8*inch
    parameters = [
        "Nitrogen (N): 90 mg/kg",
        "Phosphorus (P): 42 mg/kg",
        "Potassium (K): 43 mg/kg",
        "pH: 6.5",
        "Temperature: 20°C",
        "Humidity: 82%",
        "Rainfall: 202 mm",
        "Organic Matter: 2.5%",
        "EC: 0.45 dS/m"
    ]
    
    for param in parameters:
        c.drawString(1.2*inch, y_position, param)
        y_position -= 0.25*inch
    
    # Recommendations
    c.setFont("Helvetica-Bold", 12)
    c.drawString(1*inch, y_position - 0.3*inch, "RECOMMENDATIONS:")
    
    c.setFont("Helvetica", 9)
    y_position -= 0.6*inch
    recommendations = [
        "Based on the soil analysis, the following crops are recommended:",
        "1. Rice - Suitable for monsoon season",
        "2. Wheat - Good for winter season",
        "3. Maize - Can be grown in summer with irrigation",
        "",
        "Fertilizer Recommendations:",
        "- Apply balanced NPK fertilizer",
        "- Ensure proper water management",
        "- Maintain soil pH between 6.0-7.0"
    ]
    
    for rec in recommendations:
        c.drawString(1.2*inch, y_position, rec)
        y_position -= 0.2*inch
    
    c.save()
    print(f"Sample PDF created: {filename}")

if __name__ == "__main__":
    create_sample_soil_report()
