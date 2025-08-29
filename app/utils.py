# app/utils.py
from io import BytesIO
import PyPDF2

async def read_upload_file(upload_file):
    """Retorna (texto, filename) a partir de UploadFile"""
    data = await upload_file.read()
    fname = upload_file.filename.lower()
    if fname.endswith(".txt"):
        return data.decode("utf-8", errors="ignore")
    elif fname.endswith(".pdf"):
        reader = PyPDF2.PdfReader(BytesIO(data))
        text = ""
        for p in reader.pages:
            page_text = p.extract_text()
            if page_text:
                text += page_text + "\n"
        return text
    else:
        raise ValueError("Formato não suportado")
