# 🤖 Industrial GenAI Assistant

> **Assistente técnico inteligente para consulta de lições aprendidas industriais**, alimentado por Google Gemini e arquitetura RAG (Retrieval-Augmented Generation).

---

## 📋 Visão Geral

O **Industrial GenAI Assistant** é uma aplicação de IA conversacional voltada para o ambiente industrial, que permite a engenheiros e técnicos consultarem uma base de conhecimento de **lições aprendidas** de forma natural e eficiente.

Em vez de vasculhar manualmente pilhas de relatórios em PDF, o usuário descreve um problema técnico e o assistente encontra e sintetiza as informações mais relevantes da base de documentos — com raciocínio técnico e linguagem clara.

### Caso de Uso Principal

> *"A bomba centrífuga BC-201 apresentou vibração excessiva. O que dizem os relatórios anteriores sobre este tipo de falha?"*

O assistente recupera os trechos mais relevantes dos PDFs indexados e gera uma resposta técnica contextualizada usando o **Gemini 2.5 Flash**.

---

## 🏗️ Arquitetura

```
┌─────────────────────────────────────────────────────────────┐
│                     PIPELINE DE DADOS                       │
│                                                             │
│   data/*.pdf  ──►  PyPDFLoader  ──►  Text Splitter         │
│                                         │                   │
│                                    chunks (1000 tok)        │
│                                         │                   │
│                              Gemini Embeddings API          │
│                                         │                   │
│                                    ChromaDB  (local)        │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                   PIPELINE DE CONSULTA (RAG)                │
│                                                             │
│  Usuário ──► Streamlit UI ──► Retriever (ChromaDB)          │
│                                    │                        │
│                              Top-K chunks                   │
│                                    │                        │
│                         Prompt Template + LLM               │
│                           (Gemini 2.5 Flash)                │
│                                    │                        │
│                          Resposta técnica                   │
└─────────────────────────────────────────────────────────────┘
```

### Stack Tecnológica

| Componente | Tecnologia |
|---|---|
| Interface | [Streamlit](https://streamlit.io/) |
| LLM | Google Gemini 2.5 Flash (`gemini-2.5-flash`) |
| Embeddings | Google Gemini Embeddings (`models/gemini-embedding-001`) |
| Orquestração RAG | [LangChain](https://python.langchain.com/) |
| Banco de Vetores | [ChromaDB](https://www.trychroma.com/) (persistência local) |
| Carregamento de PDF | `langchain-community` → `PyPDFLoader` |
| Chunking | `RecursiveCharacterTextSplitter` (chunk: 1000 / overlap: 200) |
| Variáveis de ambiente | `python-dotenv` |

---

## 📁 Estrutura do Projeto

```
industrial-genai-assistant/
│
├── src/
│   ├── app.py            # Interface Streamlit + pipeline RAG (ponto de entrada)
│   └── ingest.py         # Script de ingestão e indexação de PDFs no ChromaDB
│
├── data/                 # PDFs de lições aprendidas (não versionados — ver .gitignore)
│   ├── licao_aprendida_bomba_centrifuga.pdf
│   ├── licao_aprendida_valvula_controle.pdf
│   ├── licao_aprendida_motor_compressor.pdf
│   └── licao_aprendida_trocador_calor.pdf
│
├── scripts/
│   └── generate_test_pdfs.py  # Gerador de PDFs de teste com dados industriais realistas
│
├── chroma_db/            # Banco de vetores persistido (gerado pelo ingest.py, não versionado)
├── docs/                 # Documentação adicional (a ser preenchida)
│
├── .env                  # Variáveis de ambiente (não versionado)
├── .gitignore
├── requirements.txt
└── README.md
```

---

## 🚀 Instalação e Configuração

### Pré-requisitos

- Python 3.10+
- Chave de API do Google AI Studio ([obter aqui](https://aistudio.google.com/app/apikey))

### 1. Clonar o repositório

```bash
git clone https://github.com/seu-usuario/industrial-genai-assistant.git
cd industrial-genai-assistant
```

### 2. Criar e ativar o ambiente virtual

```bash
# Windows
python -m venv .venv
.venv\Scripts\Activate.ps1

# Linux / macOS
python -m venv .venv
source .venv/bin/activate
```

### 3. Instalar as dependências

```bash
pip install -r requirements.txt
```

### 4. Configurar a chave de API

Crie o arquivo `.env` na raiz do projeto:

```env
GOOGLE_API_KEY=sua_chave_api_aqui
```

> ⚠️ **Nunca** versione o arquivo `.env`. Ele já está incluído no `.gitignore`.

---

## ▶️ Como Usar

### Passo 1 — Adicionar documentos à base de conhecimento

Coloque seus arquivos PDF na pasta `data/`. Eles podem ser relatórios de manutenção, lições aprendidas, manuais técnicos, procedimentos operacionais, etc.

Para gerar PDFs de teste com dados industriais realistas (4 relatórios simulados), execute:

```bash
python scripts/generate_test_pdfs.py
```

Isso criará 4 PDFs em `data/` cobrindo:
- Falha em rolamento de bomba centrífuga
- Vazamento em válvula de controle de pressão (linha de vapor)
- Queima de motor elétrico de compressor por sobrecarga
- Corrosão em trocador de calor casco-tubo

### Passo 2 — Indexar os documentos (ingestão)

```bash
python src/ingest.py
```

Este script:
1. Lê todos os PDFs em `data/`
2. Divide o texto em chunks de 1000 tokens (overlap de 200)
3. Gera embeddings via API do Google Gemini
4. Persiste os vetores no ChromaDB em `chroma_db/`

> ✅ Execute novamente sempre que adicionar ou remover documentos da base.

### Passo 3 — Iniciar a aplicação

```bash
streamlit run src/app.py
```

A interface estará disponível em `http://localhost:8501`.

---

## 💡 Como Funciona (RAG em Detalhe)

O fluxo de uma consulta segue os seguintes passos:

1. **Usuário** digita a descrição de um problema técnico na interface Streamlit.
2. **Retriever**: o texto da pergunta é convertido em embedding e comparado aos vetores no ChromaDB. Os `k` chunks mais similares são recuperados.
3. **Prompt**: os chunks recuperados são inseridos como contexto em um prompt estruturado junto à pergunta original.
4. **LLM**: o Gemini 2.5 Flash processa o prompt e gera uma resposta técnica e concisa, limitada ao conhecimento presente nos documentos.
5. **Resposta**: exibida na interface com formatação Markdown.

Se a resposta não estiver nos documentos indexados, o assistente informa explicitamente que não encontrou a informação na base de conhecimento.

---

## 📄 Base de Conhecimento (PDFs de Exemplo)

Os PDFs de demonstração são gerados pelo `scripts/generate_test_pdfs.py` e simulam relatórios formais de gestão de ativos industriais:

| Arquivo | Equipamento | Evento | Documentos Nº |
|---|---|---|---|
| `licao_aprendida_bomba_centrifuga.pdf` | Bomba Centrífuga BC-201 | Falha prematura em rolamento SKF 6310 por lubrificação inadequada | LA-MAINT-2024-031 |
| `licao_aprendida_valvula_controle.pdf` | Válvula de Controle PCV-104 | Vazamento de vapor pela gaxeta do haste após 6 anos de serviço | LA-INST-2024-018 |
| `licao_aprendida_motor_compressor.pdf` | Compressor CP-01 / Motor WEG 75kW | Queima de motor por sobrecarga térmica causada por filtros saturados + alarmes ignorados | LA-ELET-2024-007 |
| `licao_aprendida_trocador_calor.pdf` | Trocador de Calor HE-302 | Corrosão severa por frestas e MIC por falta de controle da qualidade da água | LA-INTEG-2024-055 |

---

## 🔧 Dependências

```txt
langchain                  # Framework de orquestração LLM
langchain-community        # Integrações (PyPDFLoader, ChromaDB)
langchain-google-genai     # Integração com Google Gemini (LLM + Embeddings)
chromadb                   # Banco de vetores local persistente
pypdf                      # Leitura e extração de texto de PDFs
python-dotenv              # Carregamento de variáveis de ambiente
streamlit                  # Interface web interativa
```

---

## 🔒 Segurança e .gitignore

Os seguintes artefatos são ignorados pelo Git:

| Item | Motivo |
|---|---|
| `.env` | Contém a chave de API — nunca versionar |
| `data/*.pdf` | PDFs de dados — gerados localmente ou confidenciais |
| `chroma_db/` | Banco de vetores — gerado automaticamente pelo `ingest.py` |
| `.venv/` | Ambiente virtual Python — não deve ser versionado |
| `__pycache__/`, `*.pyc` | Cache do Python |

---

## 📌 Próximos Passos / Roadmap

- [ ] Suporte a múltiplos tipos de documento (DOCX, TXT, HTML)
- [ ] Filtro por equipamento, área ou data na interface
- [ ] Exibição das fontes (nome do PDF e página) junto à resposta
- [ ] Integração com sistemas CMMS (ex: SAP-PM) via API
- [ ] Autenticação de usuários para acesso à base de conhecimento
- [ ] Deploy em nuvem (Google Cloud Run / Streamlit Cloud)
- [ ] Histórico de conversas persistido

---

## 📜 Licença

Este projeto está licenciado sob os termos do arquivo [LICENSE](./LICENSE).

---

> Desenvolvido com ❤️ para equipes de manutenção e engenharia industrial.