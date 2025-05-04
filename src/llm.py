from openai import OpenAI
import os
from dotenv import load_dotenv
from datetime import datetime
load_dotenv()
aux_key = os.environ["OPEN_AI"]

client = OpenAI(api_key=aux_key)



def merge_obj_gpt(contexto):
    prompt = f"""
Você é um assistente digital que trabalha com dados extraidos de imagens. Você irá receber uma lista de objetos contendo diversas extrações do mesmo documento. Seu dever é juntar tudo em unico objeto JSON com as informações corretas. Coloque as datas no formato YYYY-MM-DD.
Segue a lista de extração:
{contexto}
"""
    resposta = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Você é um assistente que segue instruções."},
            {"role": "user", "content": prompt}
        ],
        temperature=0
    )

    return resposta.choices[0].message.content.strip()

def gerar_resposta_sql(contexto):
    prompt = f"""
Você é um assistente de banco de dados. Você irá receber como contexto uma query de um banco de dados. Seu dever é explicar o resultado em linguagem natural, ou seja, deve resumir as informações da tabela que voce ira receber. Você não deve explicar o que é a tabela, mas sim os dados que estão nela. Você irá receber uma tabela com 10 registros, resuma-os 10 em linguagem natural. Você também pode receber uma resposta no formato de um numero, isso representa a resposta de um contador quando você receber isso simplesmente retorne o numero.
Contexto:
{contexto}
Sua resposta:
"""
    resposta = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Você é um assistente interpreta gera SQL com precisão."},
            {"role": "user", "content": prompt}
        ],
        temperature=0
    )

    return resposta.choices[0].message.content.strip()


def gerar_query_sql(pergunta_usuario, estrutura_bd):
    prompt = f"""
Você é um assistente que converte perguntas em linguagem natural para SQL, mais especificamente para um banco de dados em postgreSQL. Lembre-se, a pessoa pode digitar os nomes errados, então seu filtro deve ser com a tag iLike, para encontrar nomes similares e sem ser case sensitive .Lembre sempre de usar as variáveis do map. Lembrando que hoje é dia {datetime.now()}, já coloque as datas com os dias corretos. Para contadores, utilize a chave primária ao invés do *. Sempre que a pergunta não for um contador, ou seja, sempre que o desejo é ver uma planilha do banco de dados, você deve mostrar somente os 10 ultimos registros.

Estrutura do banco de dados:
{estrutura_bd}

Pergunta: {pergunta_usuario}
Query SQL:"""

    resposta = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Você é um assistente que gera SQL com precisão."},
            {"role": "user", "content": prompt}
        ],
        temperature=0
    )

    return resposta.choices[0].message.content.strip()



prompt_rg = f"""
Você irá receber um documento referente a um documento de identidade brasileiro que foi autorizado pelo titular a extração dos dados utilizando IA. Sua função é extrair as seguintes informações do documento e colocar em formato json: Nome, Registro Geral, data de nascimento, nome da mãe, nacionalidade, Estado, cpf, data de expedição. Coloque as datas no formato YYYY-MM-DD.
""" 

prompt_especialista = f"""
Você irá receber um documente referente a um diploma de especialista de uma determinada área da medicina que foi autorizada pelo titular a extração dos dados utilizando IA. Sua função é extrair as seguintes informações do documento e colocar em formato json: Nome, Especialidade, Organização, Data. Coloque as datas no formato YYYY-MM-DD.
"""

prompt_diploma = f"""
Você irá receber um documento referente a um diploma de faculdade que foi autorizado pelo titular a extração dos dados utilizando IA. Sua função é extrair as seguintes informações do documento e colocar em formato json: Nome, Universidade, data, Curso.Coloque as datas no formato YYYY-MM-DD.
""" 


prompt_crm = f"""
Você irá receber um documento público, que o titular aprovou a extração dos dados pela IA. Sua função é extrair as seguintes informações do documento e colocar em formato json: Nome, Estado, CRM, Data de inscrição. Coloque as datas no formato YYYY-MM-DD.
""" 


prompt_etico = f"""
Você irá receber um documento referente a um certificado etico profissional autorizado pelo titular a extração dos dados utilizando IA. Sua função é extrair as seguintes informações do documento e colocar em formato json: Nome, Validade, Crm, Resultado.Coloque as datas no formato YYYY-MM-DD. Classifique sempre o resultado como Ok, caso a pessoa esteja ok com a parte etica, e Nao Ok quando constar algo negativo da pessoa.
"""


prompt_debito = f"""
Você irá receber um documento referente a um certificado de debitos medicos autorizado pelo titular a extração dos dados utilizando IA. Sua função é extrair as seguintes informações do documento e colocar em formato json: Nome, Data , Crm, Resultado.Coloque as datas no formato YYYY-MM-DD. Classifique sempre o resultado como Ok, caso a pessoa esteja ok com a parte de devitos, e Nao Ok quando constar algo negativo da pessoa.
"""


def file_response(file, prompt, model_id):
    response = client.responses.create(
        model=model_id,
        input=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_file",
                        "file_id": file.id,
                    },
                    {
                        "type": "input_text",
                        "text": prompt,
                    },
                ]
            }
        ]
    )
    return response