# app/main.py
from fastapi import FastAPI, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.ai_client import generate_response
from app.utils import read_upload_file
from app.nlp import classify_by_rules

app = FastAPI(title="AutoU Email Classifier")

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

    conteudo = ""
    if texto:
        conteudo += texto + "\n"
    if arquivo:
        try:
            conteudo += await read_upload_file(arquivo)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

    # Classificação básica
    categoria, confianca = classify_by_rules(conteudo)

    # Resposta padrão (mais inteligente)
    if categoria == "Produtivo":
        if "status" in conteudo.lower():
            resposta = "Recebemos sua solicitação de atualização de status. Nossa equipe retornará em breve."
        elif "anexo" in conteudo.lower():
            resposta = "Recebemos seu e-mail com anexo. Vamos analisar e responder em seguida."
        else:
            resposta = "Recebemos sua solicitação. Nossa equipe analisará e retornará o mais breve possível."
    else:
        resposta = "Obrigado pela sua mensagem — não é necessária nenhuma ação no momento."

    # Geração de resposta com TTL local
    try:
        ai_resp = generate_response(conteudo, categoria)
        resposta = ai_resp
    except Exception as e:
        print("Erro ao gerar resposta:", e)
        # mantém resposta base se falhar

    return {
        "categoria": categoria,
        "confianca": round(confianca, 2),
        "resposta_sugerida": resposta
    }
