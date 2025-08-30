
---

### 📌 README para o **Backend** (`classificador-email-backend`)

```markdown
# ⚙️ Classificador de E-mails - Backend

Backend do projeto **Classificador de E-mails**, responsável por:

- Receber e processar e-mails enviados pelo usuário (texto ou PDF)  
- Classificar o e-mail como **Produtivo** ou **Improdutivo**  
- Calcular a **confiabilidade** da classificação  
- Gerar uma **resposta sugerida** usando modelos de IA  

👉 API Deploy: [classificador-email-backend.onrender.com/processar-email](https://classificador-email-backend.onrender.com/processar-email)  
👉 Frontend: [classificador-email-frontend](https://github.com/kakiih/classificador-email-frontend)

---

## 🚀 Tecnologias
- [FastAPI](https://fastapi.tiangolo.com/)
- [Uvicorn](https://www.uvicorn.org/)
- [NLTK](https://www.nltk.org/)
- [PyPDF2](https://pypi.org/project/pypdf2/)
- [Transformers](https://huggingface.co/docs/transformers/index)
- [Torch](https://pytorch.org/)
- [Mistral AI](https://docs.mistral.ai/)
- [dotenv](https://pypi.org/project/python-dotenv/)

---

## ⚙️ Configuração local

### 1. Clonar o repositório
```bash
git clone https://github.com/kakiih/classificador-email-backend.git
cd classificador-email-backend

python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows

pip install -r requirements.txt

MISTRAL_API_KEY=SUA_KEY_MISTRAL_AQUI
MISTRAL_MODEL=mistral-small-latest
LOCAL_MODEL_NAME=nicholasKluge/TeenyTinyLlama-160m
MAX_TOKENS=120

 uvicorn app.main:app --reload

