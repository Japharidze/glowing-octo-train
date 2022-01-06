from app import init_app
from app.bot import run_bot

app = init_app()

# run_bot()

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)