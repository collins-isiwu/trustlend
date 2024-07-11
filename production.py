from app import create_app
from app.environment import ProductionEnvironment

app = create_app(ProductionEnvironment)
