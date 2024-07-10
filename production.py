from app import create_app
from app.environment import ProductionEnvironment
import os

# Ensure environment variables are loaded
from dotenv import load_dotenv
load_dotenv()

app = create_app(ProductionEnvironment)

