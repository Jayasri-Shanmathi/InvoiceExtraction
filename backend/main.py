from fastapi import FastAPI, UploadFile, File, BackgroundTasks, HTTPException, Depends
from pdf2image import convert_from_bytes
from PIL import Image
from io import BytesIO
from preprocessing import preprocess_image
from llm.extraction import extract_invoice
from llm.invoice_prompt import INVOICE_EXTRACTION_PROMPT
from sqlalchemy.ext.asyncio import AsyncSession
from infrastructure.DB.connections import get_db
from infrastructure.DB.invoice_repository import save_invoice_data
from fastapi.middleware.cors import CORSMiddleware
from infrastructure.DB.invoice_repository import normalize_invoice_data
from dummy_invoice import DUMMY_INVOICE_DATA



app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/Upload-file/")
async def create_upload_file(file: UploadFile = File(...)):
    print("📥 Upload started")
    contents = await file.read()   # 👈 MUST BE FIRST
    print("📦 File fully read:", len(contents))
    if not file:
        raise HTTPException(status_code=400, detail="No file uploaded")
    
    pdf_bytes = contents
    processed_images = []

    try:
        
        if file.content_type == "application/pdf":
            images = convert_from_bytes(pdf_bytes)  
        else:
            images = [Image.open(BytesIO(pdf_bytes))]
        for img in images:
            processed_img = preprocess_image(img)
            processed_images.append(processed_img)

        gemini_output = extract_invoice(processed_images, prompt=INVOICE_EXTRACTION_PROMPT)
        #gemini_output = DUMMY_INVOICE_DATA
        return {"data": gemini_output}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    except RuntimeError as e:
       return {
        "error": "LLM_TIMEOUT",
        "message": "Invoice extraction took too long. Please try again."
    }

@app.post("/save-invoice/")
async def save_invoice(invoice_data: dict, db: AsyncSession = Depends(get_db)):
    print("📦 RAW invoice_data from frontend:")
    print(invoice_data)
    invoice_data=normalize_invoice_data(invoice_data)
    if not invoice_data:
        raise HTTPException(status_code=400, detail="No invoice data provided")
    try:
        invoice_id = await save_invoice_data(db, invoice_data)
        return {"message": "Invoice saved successfully", "invoice_header_id": invoice_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))



        """return StreamingResponse(
            zip_buffer,
            media_type="application/x-zip-compressed",
            headers={"Content-Disposition": f"attachment; filename={file.filename.split('.')[0]}_processed.zip"}
        )"""
           
           
    



    

