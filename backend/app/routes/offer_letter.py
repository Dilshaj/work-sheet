from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.schemas import OfferLetterCreate, OfferLetterResponse
from app.services.offer_letter_service import OfferLetterService
from typing import List
import os

router = APIRouter(prefix="/offer-letter")

@router.post("/", response_model=OfferLetterResponse, status_code=status.HTTP_201_CREATED)
def create_offer_letter(offer_data: OfferLetterCreate, db: Session = Depends(get_db)):
    """Admin endpoint to create/update offer letter details for an employee."""
    try:
        offer = OfferLetterService.create_offer_letter(db, offer_data)
        return offer
    except Exception as e:
        print(f"Error in create_offer_letter: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=List[OfferLetterResponse])
def get_offer_letters(skip: int = 0, limit: int = 100, project_id: str = None, db: Session = Depends(get_db)):
    """Admin endpoint to retrieve all offer letters. Optionally filter by project_id."""
    return OfferLetterService.get_all_offer_letters(db, skip=skip, limit=limit, project_id=project_id)

@router.get("/{employee_id}")
def download_offer_letter(employee_id: str, db: Session = Depends(get_db)):
    """Employee endpoint to download their offer letter as PDF."""
    print(f"DEBUG: Offer letter download request for: {employee_id}")
    if not employee_id:
        print("DEBUG: ERROR - employee_id is missing or invalid")
        raise HTTPException(status_code=400, detail="Employee ID is required")
        
    try:
        # Fetch from DB
        offer = OfferLetterService.get_offer_letter_data(db, employee_id)
        if not offer:
             print(f"DEBUG: No offer data found in DB for employee {employee_id}")
             raise HTTPException(status_code=404, detail="Offer letter record not found.")

        print(f"DEBUG: Found offer for {offer.name}, generating PDF...")
        # Generate PDF (returns path to file)
        pdf_path = OfferLetterService.generate_offer_letter_pdf(offer)
        
        if not os.path.exists(pdf_path):
             print(f"DEBUG: PDF path {pdf_path} does not exist nakon generation attempt.")
             raise Exception("File not found after generation.")

        print(f"DEBUG: PDF generated successfully at {pdf_path}. Returning response.")
        # Return as FileResponse
        return FileResponse(
            path=pdf_path,
            media_type="application/pdf",
            filename=f"Offer_Letter_{employee_id}.pdf"
        )
    except HTTPException as he:
        print(f"DEBUG: HTTPException caught: {he.detail}")
        raise he
    except Exception as e:
        print(f"DEBUG: CRITICAL ERROR during offer generation: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to generate offer letter: {str(e)}")
