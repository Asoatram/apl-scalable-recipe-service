import json

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, select

from Utils.cache import redis_cache
from models.Recipe import Recipe, RecipeIngredients, RecipeSteps, SavedRecipe
from Core.redis_client import redis_client


def make_cache_key_recipe(recipe_id: int) -> str:
    return f"recipe:{recipe_id}"

def make_cache_key_pagination(page, per_page):
    return f"page:{page}&per_page:{per_page}"

class RecipeRepository:

    @staticmethod
    @redis_cache(key_fn=lambda db, recipe_id: make_cache_key_recipe(recipe_id), ttl=600)
    async def get_recipe_details(db: AsyncSession, recipe_id: int):
        query = text("""
            SELECT * FROM get_recipe_details_json(:recipe_id)
        """)
        result = await db.execute(query, {"recipe_id": recipe_id})
        row = result.first()
        if row:
            response = {
                "recipe_id": row.recipe_id,
                "recipe_name": row.recipe_name,
                "description": row.description,
                "ingredients": row.ingredients,
                "steps": row.steps,
            }
            return response  # Just return, decorator caches this automatically
        return None

    @staticmethod
    @redis_cache(key_fn= lambda db, page, per_page: make_cache_key_pagination(page, per_page), ttl=600)
    async def get_recipe_pagination(db: AsyncSession, page: int, per_page: int):
        query = text("""
             SELECT * FROM get_recipes_paginated_json(:per_page, :page)
         """)
        result = await db.execute(query, {"per_page": per_page, "page": page})
        rows = result.fetchall()
        print(rows)
        if rows:
            return {
                "per_page": per_page,
                "page": page,
                "recipes": [
                    {
                        "id": row.recipe_id,
                        "name": row.recipe_name,
                        "description": row.description,
                        "ingredients": row.ingredients,
                        "steps": row.steps,
                    }
                    for row in rows
                ]
            }
        else:
            return {
                "per_page": per_page,
                "page": page,
                "recipes": []
            }

    @staticmethod
    async def create_recipe(db: AsyncSession, recipe_data):
        new_recipe = Recipe(recipe_name=recipe_data.title, description=recipe_data.description)
        db.add(new_recipe)
        await db.flush()  # to get new_recipe.recipeid

        ingredients = [
            RecipeIngredients(recipeid=new_recipe.recipeid, ingredientsid=ingredient_id)
            for ingredient_id in recipe_data.ingredients
        ]
        db.add_all(ingredients)

        # Insert steps with order index + description
        steps = [
            RecipeSteps(recipeid=new_recipe.recipeid,
                        description=step.description,
                        order=index + 1)
            for index, step in enumerate(recipe_data.steps)
        ]
        db.add_all(steps)

        await db.commit()
        await db.refresh(new_recipe)
        for key in redis_client.scan_iter("page:*"):
            await redis_client.delete(key)
        return new_recipe

    @staticmethod
    async def delete_recipe(db: AsyncSession, recipe_id: int):
        result = await db.execute(select(Recipe).where(Recipe.recipeid == recipe_id))
        recipe = result.scalar_one_or_none()

        if not recipe:
            raise HTTPException(status_code=404, detail="Recipe not found")

        # Delete recipe (this cascades to ingredients and steps)
        await db.delete(recipe)
        await db.commit()

        # Invalidate cache for this recipe
        key = make_cache_key_recipe(recipe_id)
        await redis_client.delete(key)

        for key in redis_client.scan_iter("page:*"):
            await redis_client.delete(key)
        return None

    @staticmethod
    async def save_recipe(db: AsyncSession, user_id:int, recipe_id: int):
        savedrecipe = SavedRecipe(userid=user_id, recipeid=recipe_id)
        db.add(savedrecipe)
        await db.commit()
        return savedrecipe
