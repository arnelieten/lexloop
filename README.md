# LexLoop

Run the LexLoop Flask app locally.

## Run locally

### 1. Open a terminal in the project folder

cd ~\lexloop

### 2. Use a virtual environment

python -m venv venv
.\venv\Scripts\Activate.ps1

### 3. Install dependencies

pip install -r requirements.txt

### 4. Download language models

python -m spacy download fr_core_news_lg
python -m spacy download en_core_web_sm

### 5. Set the Flask app

From the project root (folder that contains the lexloop package):
PowerShell: $env:FLASK_APP = "lexloop:create_app()"
Command Prompt: set FLASK_APP=lexloop:create_app()
Macos/Linux: export FLASK_APP="lexloop:create_app()"

### 6. Initialize DB

flask init-db

### 7. Start dev server

flask run