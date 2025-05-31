from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from Middleware.AuthGuard import JWTBearer
from Core.db import get_db
from Services.RecipeService import RecipeService

router = APIRouter(dependencies=[Depends(JWTBearer())])

class StepCreate(BaseModel):
    description: str

class RecipeCreate(BaseModel):
    title: str
    description: str
    ingredients: List[int]
    steps: List[StepCreate]

class RecipeTips(BaseModel):
    message: str


@router.get("/recipe/{id}")
async def get_recipe(id: int, db: AsyncSession = Depends(get_db)):
    recipe = await RecipeService.get_recipe_from_id(db, id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return recipe

@router.get("/recipes")
async def get_recipes(page: int, per_page:int ,db: AsyncSession = Depends(get_db)):
    recipes = await RecipeService.get_recipe_paginated(db, page, per_page)
    if not recipes:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return recipes

@router.post("/recipes", status_code=201)
async def create_recipe(recipe_in: RecipeCreate, db: AsyncSession = Depends(get_db)):
    print(recipe_in)
    new_recipe = await RecipeService.post_recipe(db, recipe_in)
    return {
        "recipe_id": new_recipe.recipeid,
        "title": new_recipe.recipe_name,
        "description": new_recipe.description
    }

@router.delete("/recipes/{id}")
async def delete_recipe(id: int, db: AsyncSession = Depends(get_db)):
    recipe = await RecipeService.delete_recipe(db, id)
    return {"message": "Recipe deleted"}

@router.post("/recipes/favorite", status_code=201)
async def save_recipe(user_id:int, recipe_id:int, db: AsyncSession = Depends(get_db) ):
        recipe = await RecipeService.save_recipe(db, user_id, recipe_id)
        if not recipe:
            raise HTTPException(status_code=404, detail="Recipe not found")
        return {"message": "Recipe saved"}

@router.post("/recipes/tips")
async def ask_tips(message:RecipeTips):
    response = await RecipeService.ask_for_tips(message.message)
    return response

