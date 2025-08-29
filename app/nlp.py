import re
from typing import Tuple

# palavras indicativas (comece simples)
PRODUTIVO = ["suporte","erro","problema","reclama","status","pedido","documento","anexo",
             "fatura","pagamento","cancelar","ajuda","solicitação","contrato","assinatura"]
IMPRODUTIVO = ["obrigado","obrigada","feliz natal","parabéns","boa tarde","bom dia","boa noite","gratidão"]

def normalize(text: str) -> str:
    text = text.lower()
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"[^\w\s]", " ", text)
    return text.strip()

def classify_by_rules(text: str) -> Tuple[str, float]:
    """
    Retorna (categoria, confiança) com base em palavras-chave.
    """
    t = normalize(text)
    tokens = set(t.split())  # tokens únicos

    # conta matches exatos
    p_count = sum(1 for w in PRODUTIVO if re.search(rf"\b{re.escape(w)}\b", t))
    i_count = sum(1 for w in IMPRODUTIVO if re.search(rf"\b{re.escape(w)}\b", t))

    if p_count > i_count:
        return "Produtivo", min(0.5 + p_count * 0.1, 0.95)
    if i_count > p_count:
        return "Improdutivo", min(0.5 + i_count * 0.1, 0.95)

    # fallback: se contém palavras chave fortes, considere produtivo
    for w in ["anexo", "erro", "reembolso", "contrato", "assinatura"]:
        if re.search(rf"\b{w}\b", t):
            return "Produtivo", 0.6

    return "Improdutivo", 0.5  # neutro se nada encontrado
