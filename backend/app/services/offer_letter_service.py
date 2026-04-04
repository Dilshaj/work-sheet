import os
from io import BytesIO
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from jinja2 import Environment, FileSystemLoader
from xhtml2pdf import pisa
from app.models.models import OfferLetter
from app.schemas.schemas import OfferLetterCreate
from fastapi import HTTPException

# Define BASE_DIR relative to this file's location (backend/app/services/offer_letter_service.py)
# os.path.dirname(__file__) is backend/app/services/
# os.path.dirname(...) of that is backend/app/
# os.path.dirname(...) of that is backend/ (the backend root)
BACKEND_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

# Path to templates (backend/app/templates/offer_letter)
TEMPLATE_DIR = os.path.join(BACKEND_ROOT, "app", "templates", "offer_letter")
TEMPLATE_NAME = "offer_letter.html"

# Dynamic path for deployment readiness (backend/static/logos/company_logo.jpg)
LOGO_PATH = os.path.join(BACKEND_ROOT, "static", "logos", "company_logo.jpg")

# Asset directory for saving generated PDFs (backend/static/offer_letters)
ASSETS_DIR = os.path.join(BACKEND_ROOT, "static", "offer_letters")
os.makedirs(ASSETS_DIR, exist_ok=True)

class OfferLetterService:
    @staticmethod
    def create_offer_letter(db: Session, offer_data: OfferLetterCreate):
        db_offer = db.query(OfferLetter).filter(OfferLetter.employee_id == offer_data.employee_id).first()
        if db_offer:
            db_offer.name = offer_data.employee_name
            db_offer.role = offer_data.role
            db_offer.joining_date = offer_data.joining_date
            db_offer.location = offer_data.location
            db_offer.package = offer_data.package
            db_offer.project_id = offer_data.project_id
        else:
            db_offer = OfferLetter(
                employee_id=offer_data.employee_id,
                name=offer_data.employee_name,
                role=offer_data.role,
                joining_date=offer_data.joining_date,
                location=offer_data.location,
                package=offer_data.package,
                project_id=offer_data.project_id
            )
            db.add(db_offer)
        
        db.commit()
        db.refresh(db_offer)
        return db_offer

    @staticmethod
    def get_offer_letter_data(db: Session, employee_id: str):
        offer = db.query(OfferLetter).filter(OfferLetter.employee_id == employee_id).first()
        if not offer:
            raise HTTPException(status_code=404, detail="Offer letter not found for this employee")
        return offer

    @staticmethod
    def get_all_offer_letters(db: Session, skip: int = 0, limit: int = 100, project_id: str = None):
        query = db.query(OfferLetter).order_by(OfferLetter.created_at.desc())
        if project_id:
            query = query.filter(OfferLetter.project_id == project_id)
        return query.offset(skip).limit(limit).all()

    @staticmethod
    def generate_offer_letter_pdf(offer_data: OfferLetter):
        print(f"PDF GENERATION STARTED (PISA ENGINE) for {offer_data.employee_id}")
        
        # Load Template
        template_file = os.path.join(TEMPLATE_DIR, TEMPLATE_NAME)
        print(f"DEBUG: Searching for template at: {template_file}")
        
        if not os.path.exists(template_file):
            print(f"DEBUG: CRITICAL - Template {TEMPLATE_NAME} NOT FOUND in {TEMPLATE_DIR}")
            # Try a fallback if BASE_DIR calculation was slightly off during deployment
            fallback_dir = os.path.join(os.getcwd(), "app", "templates", "offer_letter")
            print(f"DEBUG: Trying fallback path: {fallback_dir}")
            if os.path.exists(os.path.join(fallback_dir, TEMPLATE_NAME)):
                print("DEBUG: Using fallback path!")
                actual_template_dir = fallback_dir
            else:
                raise HTTPException(status_code=500, detail=f"HTML Template not found at {TEMPLATE_DIR} or {fallback_dir}")
        else:
            actual_template_dir = TEMPLATE_DIR

        env = Environment(loader=FileSystemLoader(actual_template_dir))
        template = env.get_template(TEMPLATE_NAME)
        
        # Prepare Data
        current_date_obj = datetime.now()
        expiry_date_obj = current_date_obj + timedelta(days=7)
        
        context = {
            "employee_name": offer_data.name,
            "employee_id": offer_data.employee_id,
            "role": offer_data.role,
            "joining_date": offer_data.joining_date,
            "location": offer_data.location,
            "package": offer_data.package,
            "date": current_date_obj.strftime("%B %d, %Y"),
            "expiry_date": expiry_date_obj.strftime("%B %d, %Y"),
            "logo_path": "file:///" + LOGO_PATH.replace("\\", "/")
        }
        
        # Render HTML
        html_content = template.render(context)
        
        try:
            # Temporary file to save the PDF
            temp_pdf = os.path.join(ASSETS_DIR, f"Offer_Letter_{offer_data.employee_id}.pdf")
            os.makedirs(ASSETS_DIR, exist_ok=True)
            
            # Generate PDF using xhtml2pdf (pisa)
            with open(temp_pdf, "wb") as f:
                pisa_status = pisa.CreatePDF(html_content, dest=f)
            
            if pisa_status.err:
                raise Exception(f"xhtml2pdf encountered {pisa_status.err} errors")
                
            if not os.path.exists(temp_pdf):
                raise Exception("PDF file was not created successfully")
                
            print(f"PDF GENERATED SUCCESSFULLY: {temp_pdf}")
            return temp_pdf
        except Exception as e:
            print(f"PDF Generation Error: {e}")
            import traceback
            traceback.print_exc()
            raise HTTPException(status_code=500, detail=f"Failed to generate professional PDF: {str(e)}")
