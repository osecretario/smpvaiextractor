from fastapi import FastAPI, Body, File, UploadFile
from fastapi.responses import RedirectResponse
from .helpers import get_gpt_response
from typing import Any, List
from openai import OpenAI
from .functions import converter_para_json, extrair_conteudo_json, get_query
from .llm import prompt_crm, prompt_debito, prompt_diploma, prompt_especialista, prompt_etico, prompt_rg, gerar_query_sql, merge_obj_gpt, gerar_resposta_sql, file_response
from .bd import estrutura_bd
import fitz
import psycopg2
import psycopg2.extras
import json
import io
from PIL import Image
import io
import traceback
import os
import time
from fastapi.middleware.cors import CORSMiddleware
from .functions import encode_image
import requests
import os
from dotenv import load_dotenv
import uuid
load_dotenv()
aux_key = os.environ["OPEN_AI"]
client = OpenAI(api_key=aux_key)
origins = ['https://localhost:3000', 'https://localhost:8080','https://smpvaiextractor-906272597071.us-central1.run.app']
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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



@app.post("/sql_assistant")
async def sql_assistant(payload: Any = Body(None)):
    pergunta = payload['pergunta']
    assistant_id = payload['assistant_id']
    thread_id = payload['thread_id']
    # Inicia thread
    print ('Vou começar o run create and run')
    if len(thread_id) == 0:
        print ('entrei no len == 0')
        
        run = client.beta.threads.create_and_run(
            assistant_id=assistant_id,
            thread={
                "messages": [
                {"role": "user", "content": pergunta}
                ]
            }
        )
        thread_id = run.thread_id
        run_id = run.id
    else:
        message = client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=pergunta
        )
        run = client.beta.threads.runs.create_and_poll(
            thread_id=thread_id,
            assistant_id=assistant_id,
        )
        run_id = run.id


    print (" Vou começar o while")
    # Aguarda o Assistant terminar de processar
    while True:
        print ("Entrei no while True")
        run_status = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run_id)
        if run_status.status in ["completed", "requires_action", "failed"]:
            break
        time.sleep(1)

    # Caso seja uma function call
    if run_status.status == "requires_action":
        print ("entrei no status requires action")
        tool_call = run_status.required_action.submit_tool_outputs.tool_calls[0]
        query = eval(tool_call.function.arguments)["query"]


        # Chamada ao seu backend Flask que executa a query
        print ("Query é:", query)

        aux_url = os.environ['PG_URL']
        pg_uri = aux_url
        conn = psycopg2.connect(pg_uri)
        cursor = conn.cursor()
        cursor.execute(query)
        resposta_backend = cursor.fetchall()
        # Retorna resultado da função para o Assistant
        print ("Vou começar o run submit tull")
        client.beta.threads.runs.submit_tool_outputs(
            thread_id=thread_id,
            run_id=run_id,
            tool_outputs=[
                {
                    "tool_call_id": tool_call.id,
                    "output": resposta_backend
                }
            ]
        )

        # Espera o Assistant responder com base nos dados retornados
        while True:
            print ("Entrei no segundo while")
            final_run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run_id)
            if final_run.status == "completed":
                break
        time.sleep(1)

    # Em qualquer caso (com ou sem função), pega a resposta final
    messages = client.beta.threads.messages.list(thread_id=thread_id)
    print("\nResposta do Assistant:")
    print(messages.data[0].content[0].text.value)
    dict_final = {
        "resposta" : messages.data[0].content[0].text.value,
        "thread_id" : thread_id
    }
    return json.loads(json.dumps(dict_final))


@app.post("/make_query")
async def make_query(payload: Any = Body(None)):
    query = payload['pergunta']
    aux_url = os.environ['PG_URL']
    pg_uri = aux_url
    conn = psycopg2.connect(pg_uri)
    cursor = conn.cursor()
    cursor.execute(query)
    
    return cursor.fetchall()


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


@app.post("/gpt_by_assistant")
async def gpt_assistant(payload: Any = Body(None)):
    try:
        input = payload['pergunta']
        gerador_sql_id = payload['gerador_sql_id']
        gerador_resposta_id = payload['gerador_resposta_id']

        assistant_url = "https://api.openai.com/v1/threads/runs"
        headers = {
            "Content-Type" : "application/json",
            "Authorization" : f"Bearer {aux_key}",
            "OpenAI-Beta" : "assistants=v2"

        }
        data = {
            "assistant_id": gerador_sql_id ,
            "thread": {
                "messages": [
                {
                    "role": "user","content":f"{input}"
                }
                ]
            }
        }

        response = requests.post(url=assistant_url, headers=headers, json=data)
        obj_resposta = response.json()
        
        thread_id = obj_resposta['thread_id']
        run_id = obj_resposta['id']
        url_status = f"https://api.openai.com/v1/threads/{thread_id}/runs/{run_id}"

        status = "false"

        while status != "completed":
            print ('entrei no while')
            chamada = requests.get(url=url_status, headers=headers)
            chamada = chamada.json()
            status = chamada['status']
            print (status)
            if status != "queued" and status != "in_progress" and status != "completed":
                return f"Ops, tivemos um erro por aqui. Tente novamente mais tarde."
            
            time.sleep(1)




        url_resposta = f"https://api.openai.com/v1/threads/{thread_id}/messages"
        response_2 = requests.get(url=url_resposta, headers=headers)
        obj_aux = response_2.json()
        resposta_final = obj_aux['data'][0]['content'][0]['text']['value']
        resposta_final = f"{resposta_final}".replace("```sql","").replace("```","")
        print (resposta_final)
        final = get_query(resposta_final)

        data_2 = {
            "assistant_id": gerador_resposta_id ,
            "thread": {
                "messages": [
                {
                    "role": "user","content":f"{final}"
                }
                ]
            }
        }

        response_final = requests.post(url=assistant_url, headers=headers, json=data_2)
        obj_resposta_final = response_final.json()
        thread_id_final = obj_resposta_final['thread_id']
        run_id_final = obj_resposta_final['id']
        url_status = f"https://api.openai.com/v1/threads/{thread_id_final}/runs/{run_id_final}"

        status = "false"

        while status != "completed":
            print ('entrei no while')
            chamada = requests.get(url=url_status, headers=headers)
            chamada = chamada.json()
            status = chamada['status']
            print (status)
            if status != "queued" and status != "in_progress" and status != "completed":
                return f"Ops, tivemos um erro por aqui. Tente novamente mais tarde."
            
            time.sleep(1)


        url_resposta_final = f"https://api.openai.com/v1/threads/{thread_id_final}/messages"
        response_final_2 = requests.get(url=url_resposta_final, headers=headers)
        obj_aux_final = response_final_2.json()
        resposta_final_2 = obj_aux_final['data'][0]['content'][0]['text']['value']
        return resposta_final_2
    except Exception as e:
                    print(e)
                    
                    return str(e)
    

