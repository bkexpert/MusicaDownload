# MusiFlow

Projeto acadêmico de um conversor/download de mídia com interface web em HTML/CSS/JavaScript e backend em Python/Flask.

## O que o projeto faz

- recebe uma URL direta para um arquivo de mídia;
- identifica o tipo e tamanho do arquivo;
- permite escolher MP3 ou MP4;
- permite escolher qualidade de áudio;
- usa FFmpeg para conversão;
- devolve o arquivo convertido para o navegador;
- possui interface responsiva.

> **Importante:** o backend foi intencionalmente projetado para trabalhar com **URLs diretas de arquivos de mídia**. Não inclui mecanismos para contornar DRM, autenticação, paywalls ou restrições de plataformas. Use somente conteúdos para os quais você tenha autorização.

## Estrutura

```text
musiflow/
├── backend/
│   ├── app.py
│   └── requirements.txt
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── app.js
└── README.md
```

## Requisitos

- Python 3.10+
- FFmpeg instalado e disponível no PATH
- Navegador moderno

### Verificar FFmpeg

```bash
ffmpeg -version
```

## 1. Instalar dependências

No Windows:

```powershell
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

No macOS/Linux:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 2. Iniciar o backend

```bash
python app.py
```

O servidor ficará em:

```text
http://127.0.0.1:5000
```

## 3. Abrir o frontend

Abra:

```text
frontend/index.html
```

no navegador.

Para um ambiente de desenvolvimento mais organizado, você também pode servir a pasta frontend:

```bash
cd frontend
python -m http.server 5500
```

Depois acesse:

```text
http://127.0.0.1:5500
```

## GitHub

Crie um repositório chamado `musiflow` e envie os arquivos:

```bash
git init
git add .
git commit -m "Projeto inicial MusiFlow"
git branch -M main
git remote add origin SEU_REPOSITORIO
git push -u origin main
```

## Observação para a apresentação

O projeto demonstra uma arquitetura simples:

**Frontend → API Flask → Download da mídia autorizada → FFmpeg → arquivo MP3/MP4 → navegador**

Para uma versão de produção seriam necessários autenticação, fila de processamento, limites por usuário, armazenamento temporário, logs, validação de segurança de URLs e proteção contra SSRF.
