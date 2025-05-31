from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from models import Base, User, Ingredients

class Recipe(Base):
    __tablename__ = "recipe"
    recipeid = Column(Integer, primary_key=True, index=True, autoincrement=True)
    recipe_name = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(String, nullable=False, index=True)
    ingredients = relationship("RecipeIngredients", back_populates="recipe", cascade="all, delete")
    steps = relationship("RecipeSteps", back_populates="recipe", cascade="all, delete")
    saved_by = relationship("SavedRecipe", back_populates="recipe", cascade="all, delete")

class RecipeIngredients(Base):
    __tablename__ = "recipeingredients"
    recipeingredientsid = Column(Integer, primary_key=True, index=True, autoincrement=True)
    recipeid = Column(Integer, ForeignKey("recipe.recipeid"), nullable=False)
    ingredientsid = Column(Integer, ForeignKey("ingredients.ingredientsid"), nullable=False)
    recipe = relationship("Recipe", back_populates="ingredients")
    ingredient = relationship("Ingredients")

class RecipeSteps(Base):
    __tablename__ = "recipesteps"
    recipestepsid = Column(Integer, primary_key=True, index=True, autoincrement=True)
    recipeid = Column(Integer, ForeignKey("recipe.recipeid"), nullable=False)
    description = Column(String, nullable=False)
    order = Column(Integer, nullable=False)
    recipe = relationship("Recipe", back_populates="steps")



class SavedRecipe(Base):
    __tablename__ = "savedrecipe"

    savedrecipeid = Column(Integer, primary_key=True, index=True, autoincrement=True)
    recipeid = Column(Integer, ForeignKey("recipe.recipeid"), nullable=False)
    userid = Column(Integer, ForeignKey("users.userid"), nullable=False)
    recipe = relationship("Recipe", back_populates="saved_by")  # ✅ Match this name
    user = relationship("User", back_populates="saved_recipes")
