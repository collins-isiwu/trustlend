from app import create_app
from app.environment import DevelopmentEnvironment

app = create_app(DevelopmentEnvironment)

if __name__ == "__main__":
    app.run(debug=True)