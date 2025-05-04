import json
import base64
import fitz  # PyMuPDF
import os
from dotenv import load_dotenv
import re
import psycopg2
import psycopg2.extras
from fpdf import FPDF

load_dotenv()
aux_url = os.environ['PG_URL']

def extrair_conteudo_json(texto):
    # Expressão regular para capturar o conteúdo entre a primeira abertura e o último fechamento de chaves
    match = re.search(r"\{.*\}", texto, re.DOTALL)
    if match:
        return json.loads(match.group(0))
    else:
        print("Não foi possível encontrar um JSON no texto.")
        return None
    
def converter_para_json(dado_str):
    # Remove a parte do markdown para ficar apenas o conteúdo JSON
    dado_str_limpo = dado_str.strip("```json\n").strip("\n```")
    
    # Converte a string para um objeto JSON
    try:
        objeto_json = json.loads(dado_str_limpo)
        return objeto_json
    except json.JSONDecodeError as e:
        print(f"Erro na conversão: {e}")
        return None


def extract_images_from_pdf(pdf_path):
    images_base64 = []

    # Abre o PDF
    doc = fitz.open(pdf_path)

    # Itera pelas páginas do PDF
    for page_num in range(doc.page_count):
        page = doc.load_page(page_num)
        img_list = page.get_images(full=True)
        
        # Para cada imagem encontrada na página
        for img_index, img in enumerate(img_list):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            
            # Codifica a imagem em base64
            image_base64 = base64.b64encode(image_bytes).decode('utf-8')
            images_base64.append(image_base64)

    return images_base64

def encode_image(image_path):
    # Verifica se o arquivo é um PDF
    if image_path.lower().endswith('.pdf'):
        # Extrai as imagens do PDF
        images_base64 = extract_images_from_pdf(image_path)
        return images_base64
    else:
        # Se for uma imagem normal, converte diretamente para base64
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
        
def get_query (query):
    pg_uri = aux_url
    conn = psycopg2.connect(pg_uri)
    cursor = conn.cursor()
    cursor.execute(query)
    
    return cursor.fetchall()


