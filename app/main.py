# app/main.py
from fastapi import FastAPI, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.ai_client import generate_response
from app.utils import read_upload_file
import json
import re

app = FastAPI(title="Classificador de email")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "API funcionando"}

@app.post("/processar-email/")
async def processar_email(
    texto: str = Form(None),
    arquivo: UploadFile = None
):
    if not texto and not arquivo:
        raise HTTPException(status_code=400, detail="Enviar 'texto' ou 'arquivo'")

    # Ler conteúdo do email
    conteudo = ""
    if texto:
        conteudo += texto + "\n"
    if arquivo:
        try:
            conteudo += await read_upload_file(arquivo)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

    # ===== Classificação via IA com confiança =====
    try:
        prompt_classificacao = f"""
Você é um assistente profissional que analisa e-mails. 
Seu objetivo é determinar se um e-mail é Produtivo ou Improdutivo e fornecer um grau de produtividade como número decimal entre 0.1 e 0.9.

- Produtivo: e-mails que exigem ação profissional (solicitações, dúvidas sobre sistemas, atualizações de status, problemas, contratos, pagamentos, etc.).
- Improdutivo: e-mails triviais ou que não exigem ação (mensagens de bom dia, felicitações, agradecimentos, spam).

Analise o e-mail abaixo e responda apenas em JSON com os campos:
{{"categoria": "Produtivo" ou "Improdutivo", "confianca": decimal de 0.1 a 0.9}}

E-mail:
\"\"\"{conteudo}\"\"\"
"""

        resposta_ia = generate_response(prompt_classificacao, category="classificacao").strip()

        # Extrai o JSON mesmo que venha algum texto extra
        match = re.search(r"\{.*\}", resposta_ia, re.DOTALL)
        if match:
            dados = json.loads(match.group(0))
            categoria = str(dados.get("categoria", "Improdutivo")).capitalize()
            confianca = float(dados.get("confianca", 0.5))
            confianca = max(0.1, min(confianca, 0.9))
        else:
            categoria = "Improdutivo"
            confianca = 0.5

    except Exception as e:
        print("Erro ao classificar com IA, fallback:", e)
        categoria = "Improdutivo"
        confianca = 0.5

    # ===== Geração da resposta automática =====
    try:
        ai_resp = generate_response(conteudo, categoria)
        resposta = ai_resp
    except Exception as e:
        print("Erro ao gerar resposta:", e)
        # fallback se IA falhar
        if categoria == "Produtivo":
            resposta = "Recebemos sua solicitação. Nossa equipe analisará e retornará o mais breve possível."
        else:
            resposta = "Obrigado pela sua mensagem — não é necessária nenhuma ação no momento."

    return {
        "categoria": categoria,
        "confianca": round(confianca, 2),
        "resposta_sugerida": resposta
    }
