from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from models import Base

class Pantry(Base):
    __tablename__ = "pantry"
    pantryid = Column(Integer, primary_key=True, index=True, autoincrement=True)
    userid = Column(Integer, ForeignKey("users.userid"), nullable=False)

    user = relationship("User", back_populates="pantries")
    pantry_ingredients = relationship("PantryIngredients", back_populates="pantry")

class PantryIngredients(Base):
    __tablename__ = "pantryingredients"

    pantryingredientsid = Column(Integer, primary_key=True, index=True, autoincrement=True)
    pantryid = Column(Integer, ForeignKey("pantry.pantryid"), nullable=False)
    ingredientsid = Column(Integer, ForeignKey("ingredients.ingredientsid"), nullable=False)
    quantity = Column(Integer, nullable=False)
    pantry = relationship("Pantry", back_populates="pantry_ingredients")
    ingredient = relationship("Ingredients")