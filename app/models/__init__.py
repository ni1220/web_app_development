from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from .user import User
from .recipe import Recipe
from .ingredient import Ingredient
from .step import Step
from .favorite import Favorite
