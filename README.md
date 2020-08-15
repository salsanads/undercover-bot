# Undercover Bot
[![Python 3.8](https://img.shields.io/badge/python-3.8-blue.svg)](https://www.python.org/downloads/release/python-380/)

A bot (hopefully) for playing Undercover in Discord.

## Development Guide
1. Create a virtual environment
```
python -m venv venv
```

2. Activate the virtual environment
```
source venv/bin/activate
```

3. Install the dependencies
```
pip install -r requirements.txt
```

4. Setup pre-commit hook
```
pre-commit install
```

5. Copy the `.env.example` file with new name `.env`
```
cp .env.example .env
```

6. Adjust the `.env` file content accordingly

7. Run tests
```
pytest
```

8. Run the bot
```
python run.py
```
