from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from models import Base

class Ingredients(Base):
    __tablename__ = "ingredients"

    ingredientsid = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, unique=True, nullable=False, index=True)
    recipeingredients = relationship("RecipeIngredients", back_populates="ingredient")
