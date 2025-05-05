from fastapi import FastAPI, Body, File, UploadFile
from fastapi.responses import RedirectResponse
from .helpers import get_gpt_response
from typing import Any, List
from openai import OpenAI
from .functions import converter_para_json, extrair_conteudo_json, get_query
from .llm import prompt_crm, prompt_debito, prompt_diploma, prompt_especialista, prompt_etico, prompt_rg, gerar_query_sql, merge_obj_gpt, gerar_resposta_sql, file_response
from .bd import estrutura_bd
import fitz
import json
import io
from PIL import Image
import io
import os
from fastapi.middleware.cors import CORSMiddleware
from .functions import encode_image
import requests
import os
from dotenv import load_dotenv
import uuid
load_dotenv()
aux_key = os.environ["OPEN_AI"]
client = OpenAI(api_key=aux_key)
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['null'],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")   


async def root():
    return RedirectResponse("/docs")



def convert_pdf_to_images(pdf_bytes: bytes) -> List[Image.Image]:
    """Converte um PDF em uma lista de imagens RGB usando PyMuPDF."""
    images = []
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    for page in doc:
        pix = page.get_pixmap()
        img_bytes = pix.tobytes("png")
        img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
        images.append(img)
    
    return images


@app.post("/upload-mixed-to-pdf/")
async def upload_mixed_to_pdf(files: List[UploadFile] = File(...)):
    images = []

    for file in files:
        contents = await file.read()
        filename = file.filename.lower()

        try:
            if filename.endswith('.pdf'):
                pdf_images = convert_pdf_to_images(contents)
                images.extend(pdf_images)
            else:
                img = Image.open(io.BytesIO(contents)).convert("RGB")
                images.append(img)
        except Exception as e:
            return {"error": f"Erro ao processar {file.filename}: {str(e)}"}

    if not images:
        return {"error": "Nenhuma imagem válida foi enviada"}

    pdf_filename = f"{uuid.uuid4()}.pdf"
    pdf_path = f"{pdf_filename}"

    images[0].save(pdf_path, save_all=True, append_images=images[1:])

    return 

### Rotas que podem receber mais de uma imagem/arquivo

@app.post("/extract_rg")
async def extract_rg(files: List[UploadFile] = File(...)):
    print ('Entrei')
    images = []

    for file in files:
        contents = await file.read()
        filename = file.filename.lower()

        try:
            if filename.endswith('.pdf'):
                pdf_images = convert_pdf_to_images(contents)
                images.extend(pdf_images)
            else:
                img = Image.open(io.BytesIO(contents)).convert("RGB")
                images.append(img)
        except Exception as e:
            return {"error": f"Erro ao processar {file.filename}: {str(e)}"}

    if not images:
        return {"error": "Nenhuma imagem válida foi enviada"}

    pdf_filename = f"{uuid.uuid4()}.pdf"
    pdf_path = f"{pdf_filename}"

    images[0].save(pdf_path, save_all=True, append_images=images[1:])
    print ('Vou criar a file gpt')

    with open(pdf_path, "rb") as file:
        file_gpt = client.files.create(
            file=file,
            purpose="user_data"
        )


    if os.path.exists(pdf_path):
        os.remove(pdf_path)

    model_id = 'gpt-4.1-2025-04-14'
    print ('Vou gerar a resposta')
    resposta = file_response(file_gpt, prompt_rg, model_id)
    print ('gerei a resposta')
    print (resposta)
    if os.path.exists(pdf_path):
        os.remove(pdf_path)
    resposta = json.loads(resposta.json())
    resposta = resposta['output'][0]['content'][0]['text']
    obj_resposta = extrair_conteudo_json(resposta)
    return obj_resposta


@app.post("/extract_crm")
async def extract_crm(files: List[UploadFile] = File(...)):
    print ('Entrei')
    images = []

    for file in files:
        contents = await file.read()
        filename = file.filename.lower()

        try:
            if filename.endswith('.pdf'):
                pdf_images = convert_pdf_to_images(contents)
                images.extend(pdf_images)
            else:
                img = Image.open(io.BytesIO(contents)).convert("RGB")
                images.append(img)
        except Exception as e:
            return {"error": f"Erro ao processar {file.filename}: {str(e)}"}

    if not images:
        return {"error": "Nenhuma imagem válida foi enviada"}

    pdf_filename = f"{uuid.uuid4()}.pdf"
    pdf_path = f"{pdf_filename}"

    images[0].save(pdf_path, save_all=True, append_images=images[1:])
    print ('Vou criar a file gpt')

    with open(pdf_path, "rb") as file:
        file_gpt = client.files.create(
            file=file,
            purpose="user_data"
        )


    if os.path.exists(pdf_path):
        os.remove(pdf_path)

    model_id = 'gpt-4.1-2025-04-14'
    print ('Vou gerar a resposta')
    resposta = file_response(file_gpt, prompt_crm, model_id)
    print ('gerei a resposta')
    print (resposta)
    if os.path.exists(pdf_path):
        os.remove(pdf_path)
    resposta = json.loads(resposta.json())
    resposta = resposta['output'][0]['content'][0]['text']
    obj_resposta = extrair_conteudo_json(resposta)
    return obj_resposta


##### Os demais seguem 1 arquivo somente
@app.post("/extract_especialidade")
async def extract_especialidade(file: UploadFile = File(...)):
    print ('Entrei')
    contents = await file.read()

    with open(file.filename, 'wb') as f:
        f.write(contents)
    resposta_especialidade = get_gpt_response(file.filename, prompt_especialista, 'gpt-4o-mini-2024-07-18')
    resposta_especialidade = resposta_especialidade['choices'][0]['message']['content']
    json_obj_especialidade = converter_para_json(resposta_especialidade)
    if os.path.exists(file.filename):
        os.remove(file.filename)
    return json_obj_especialidade

@app.post("/extract_diploma")
async def extract_diploma(file: UploadFile = File(...)):
    print ('Entrei')
    contents = await file.read()

    with open(file.filename, 'wb') as f:
        f.write(contents)
    resposta_especialidade = get_gpt_response(file.filename, prompt_diploma, 'gpt-4o-mini-2024-07-18')
    resposta_especialidade = resposta_especialidade['choices'][0]['message']['content']
    json_obj_especialidade = converter_para_json(resposta_especialidade)
    if os.path.exists(file.filename):
        os.remove(file.filename)
    return json_obj_especialidade


@app.post("/extract_etico")
async def extract_etico(file: UploadFile = File(...)):
    print ('Entrei')
    contents = await file.read()

    with open(file.filename, 'wb') as f:
        f.write(contents)
    resposta_especialidade = get_gpt_response(file.filename, prompt_etico, 'gpt-4o-mini-2024-07-18')
    resposta_especialidade = resposta_especialidade['choices'][0]['message']['content']
    json_obj_especialidade = converter_para_json(resposta_especialidade)
    if os.path.exists(file.filename):
        os.remove(file.filename)
    return json_obj_especialidade

@app.post("/extract_debito")
async def extract_debito(file: UploadFile = File(...)):
    print ('Entrei')
    contents = await file.read()

    with open(file.filename, 'wb') as f:
        f.write(contents)
    resposta_especialidade = get_gpt_response(file.filename, prompt_debito, 'gpt-4o-mini-2024-07-18')
    resposta_especialidade = resposta_especialidade['choices'][0]['message']['content']
    json_obj_especialidade = converter_para_json(resposta_especialidade)

    if os.path.exists(file.filename):
        os.remove(file.filename)

    return json_obj_especialidade

@app.post("/extract_sql")
async def extract_sql(payload: Any = Body(None)):
    try:
        pergunta = ''
        for values in payload.values():
            pergunta+=values
        pergunta = f'{pergunta}'
    except:
        pergunta = f'{payload}'

    resposta = gerar_query_sql(pergunta, estrutura_bd)
    print (resposta)
    final = get_query(resposta)
    dict_contexto = {
        "query" : resposta,
        "resultado":final
    }
    resposta_final = gerar_resposta_sql(final)
    dict_resposta = {
        "resposta" : resposta_final
    }
    return dict_resposta


