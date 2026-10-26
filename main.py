from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from googletrans import Translator, LANGUAGES
from typing import Optional
import os

app = FastAPI(
    title="Multilingual NLP Translation API",
    description="Scalable Indian language translation API developed for SIH 2023.",
    version="1.0.0",
)

# Enable CORS for frontend consumption
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

translator = Translator()

# Request & Response schemas
class TranslationRequest(BaseModel):
    text: str = Field(..., example="Hello, welcome to India!")
    target_lang: str = Field(..., example="hi", description="ISO language code (e.g., hi, ta, te, bn, mr)")
    source_lang: Optional[str] = Field("auto", example="en", description="Source language (default 'auto')")

class TranslationResponse(BaseModel):
    original_text: str
    translated_text: str
    source_lang: str
    target_lang: str

# Serve the index.html UI at root URL
@app.get("/", response_class=FileResponse)
def read_root():
    if os.path.exists("index.html"):
        return FileResponse("index.html")
    return {
        "status": "online",
        "message": "Multilingual Translation API Ready",
        "supported_languages_count": len(LANGUAGES),
        "docs_url": "/docs"
    }

@app.get("/languages")
def get_supported_languages():
    """Returns all supported language codes and full names."""
    return {"languages": LANGUAGES}

@app.post("/translate", response_model=TranslationResponse)
def translate_text(payload: TranslationRequest):
    """
    Translates input text into the target language.
    """
    if not payload.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty.")
    
    try:
        result = translator.translate(
            payload.text,
            src=payload.source_lang,
            dest=payload.target_lang
        )
        return TranslationResponse(
            original_text=payload.text,
            translated_text=result.text,
            source_lang=result.src,
            target_lang=result.dest
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Translation failed: {str(e)}")