# Undercover Bot
[![Python 3.8](https://img.shields.io/badge/python-3.8-blue.svg)](https://www.python.org/downloads/release/python-380/)

![Undercover](https://user-images.githubusercontent.com/9564160/93617198-dbede880-f9ff-11ea-8c21-1c5e536a588d.png)

A Discord bot for playing and inspired from [Undercover ^^](https://www.producthunt.com/posts/undercover-2) game.

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
