# ia_teste.py
from app.ai_client import generate_response

email = ""
categoria = "Produtivo"

resposta = generate_response(email, categoria)
print("Resposta gerada:\n", resposta)


