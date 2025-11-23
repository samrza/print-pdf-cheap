from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from backend.impose import impose_cut_stack
import tempfile

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/impose")
async def impose_endpoint(file: UploadFile = File(...)):
    input_pdf = await file.read()

    output_stream = impose_cut_stack(input_pdf)

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    tmp.write(output_stream.read())
    tmp.close()

    return FileResponse(
        tmp.name,
        media_type="application/pdf",
        filename="output.pdf"
    )
