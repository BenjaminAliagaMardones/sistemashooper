import os
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML

def generate_order_pdf(order_data: dict, business_data: dict, client_data: dict) -> bytes:
    """
    Generates a PDF bytes object from an HTML template using WeasyPrint and Jinja2.
    """
    # Get template directory
    template_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "templates")
    
    # Initialize Jinja environment
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template("order_invoice.html")
    
    # Render template with data
    html_out = template.render(
        order=order_data,
        business=business_data,
        client=client_data
    )
    
    # Generate PDF
    pdf_bytes = HTML(string=html_out).write_pdf()
    return pdf_bytes
