# app/ai_client.py
import os
import time
from typing import Optional

from app.config import MISTRAL_API_KEY, MISTRAL_MODEL, LOCAL_MODEL_NAME, MAX_TOKENS

# remote client
mistral_available = bool(MISTRAL_API_KEY)

# import lazily to avoid failing if not installed
if mistral_available:
    try:
        from mistralai import Mistral  # official client
    except Exception as e:
        mistral_available = False
        print("Aviso: package 'mistralai' não carregado:", e)

# local model (lazy load)
_local_tokenizer = None
_local_model = None
_local_device = None

def _load_local_model():
    global _local_tokenizer, _local_model, _local_device
    if _local_tokenizer is not None and _local_model is not None:
        return
    try:
        from transformers import AutoTokenizer, AutoModelForCausalLM
        import torch
    except Exception as e:
        raise RuntimeError("Para usar o fallback local é necessário instalar 'transformers' e 'torch'") from e

    _local_device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    _local_tokenizer = AutoTokenizer.from_pretrained(LOCAL_MODEL_NAME)
    _local_model = AutoModelForCausalLM.from_pretrained(LOCAL_MODEL_NAME).to(_local_device)
    _local_model.eval()

def generate_response_with_local_ttl(email_text: str, category: str, max_tokens: int = MAX_TOKENS) -> str:
    """
    Gera resposta local usando TTL (fallback). Prompt direcionado para respostas curtas.
    """
    _load_local_model()
    prompt = (
        "Você é um assistente que responde e-mails de forma curta, objetiva e profissional.\n"
        f"Categoria: {category}\n"
        f"E-mail: {email_text}\n\n"
        "Resposta curta:"
    )

    inputs = _local_tokenizer(prompt, return_tensors="pt").to(_local_device)
    with __import__("torch").no_grad():
        outputs = _local_model.generate(
            **inputs,
            max_new_tokens=max_tokens,
            do_sample=True,
            temperature=0.25,
            top_p=0.9,
            pad_token_id=_local_tokenizer.eos_token_id,
            eos_token_id=_local_tokenizer.eos_token_id
        )
    generated = _local_tokenizer.decode(outputs[0], skip_special_tokens=True)
    # extrai só a parte após "Resposta curta:"
    if "Resposta curta:" in generated:
        return generated.split("Resposta curta:")[-1].strip()
    # fallback: remove prompt
    return generated.replace(prompt, "").strip()

def generate_response_with_mistral(email_text: str, category: str, max_tokens: int = MAX_TOKENS) -> str:
    """
    Gera resposta usando API Mistral. Cria um client temporário por chamada (seguro para concorrência).
    """
    if not MISTRAL_API_KEY:
        raise RuntimeError("MISTRAL_API_KEY não configurada")

    prompt = (
        "Você é um assistente que responde e-mails de forma curta, objetiva e profissional. "
        "Sempre finalize a resposta com uma despedida educada, seguida de:\n"
        "'Atenciosamente,\n[Seu Nome]'.\n\n"
        f"Categoria: {category}\n"
        f"E-mail: {email_text}\n\n"
        "Escreva apenas a resposta final formatada."
    )


    # usamos client por chamada com 'with' (documentação do cliente). Você também pode manter um client global.
    try:
        with Mistral(api_key=MISTRAL_API_KEY) as client:
            resp = client.chat.complete(
                model=MISTRAL_MODEL,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=0.2,
                top_p=0.9,
                stream=False,
            )
    except Exception as e:
        # propaga para o wrapper tratar (ou logar)
        raise

    # parse resposta: objeto res normalmente tem choices[0].message.content
    try:
        # objeto custom; tentamos os formatos mais prováveis
        if hasattr(resp, "choices") and len(resp.choices) > 0:
            return resp.choices[0].message.content.strip()
        if isinstance(resp, dict):
            if "choices" in resp and len(resp["choices"]) > 0:
                # choices -> message -> content
                ch = resp["choices"][0]
                if isinstance(ch.get("message"), dict):
                    return ch["message"].get("content", "").strip()
            if "outputs" in resp and len(resp["outputs"]) > 0:
                return resp["outputs"][0].get("text", "").strip()
        # fallback
        return str(resp).strip()
    except Exception:
        return str(resp).strip()

def generate_response(email_text: str, category: str, max_tokens: int = MAX_TOKENS) -> str:
    """
    Interface única: tenta Mistral (se chave configurada), senão TTL local.
    Se Mistral falhar (erro, rate limit), tenta fallback local.
    """
    # 1) se Mistral configurada, tente
    if mistral_available:
        try:
            return generate_response_with_mistral(email_text, category, max_tokens=max_tokens)
        except Exception as e:
            # log e tenta fallback
            print("Erro na chamada Mistral (fallback para local):", str(e))

    # 2) fallback local
    try:
        return generate_response_with_local_ttl(email_text, category, max_tokens=max_tokens)
    except Exception as e:
        # última tentativa: mensagem segura
        print("Erro no modelo local:", e)
        return ("Desculpe — não foi possível gerar uma sugestão agora. "
                "Você pode usar a resposta padrão do sistema.")
