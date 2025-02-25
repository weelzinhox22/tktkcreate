from src.server.api import app

# Para desenvolvimento local
if __name__ == "__main__":
    app.run()

# Para produção (Render.com)
application = app 