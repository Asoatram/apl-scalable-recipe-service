import uuid

from sqlalchemy.orm import selectinload

from models.Pantry import Pantry, PantryIngredients
from models.Ingredients import Ingredients
from sqlalchemy import select


class PantryRepository:
    @staticmethod
    async def create_pantry(db, userid):
        pantry = Pantry(userid=userid)
        db.add(pantry)
        await db.commit()
        await db.refresh(pantry)
        return pantry

    @staticmethod
    async def add_ingredient_to_pantry(db, pantryid, ingredientsid, quantity):

        result = await db.execute(select(Ingredients).where(Ingredients.ingredientsid == ingredientsid))
        ingredient = result.scalar_one_or_none()
        if not ingredient:
            return None

        pantry_ingredient = PantryIngredients(
            pantryid=pantryid,
            ingredientsid=ingredientsid,
            quantity=quantity
        )
        db.add(pantry_ingredient)
        await db.commit()
        await db.refresh(pantry_ingredient)
        return pantry_ingredient

    @staticmethod
    async def update_pantry_ingredient_by_ingredientid(db, pantryid, ingredientid, quantity):
        result = await db.execute(
            select(PantryIngredients).where(
                PantryIngredients.pantryid == pantryid,
                PantryIngredients.ingredientsid == ingredientid
            )
        )
        pantry_ingredient = result.scalar_one_or_none()
        if not pantry_ingredient:
            return None
        pantry_ingredient.quantity = quantity
        await db.commit()
        await db.refresh(pantry_ingredient)
        return pantry_ingredient

    @staticmethod
    async def delete_pantry_ingredient_by_ingredientid(db, pantryid, ingredientid):
        from models.Pantry import PantryIngredients
        result = await db.execute(
            select(PantryIngredients).where(
                PantryIngredients.pantryid == pantryid,
                PantryIngredients.ingredientsid == ingredientid
            )
        )
        pantry_ingredient = result.scalar_one_or_none()
        if not pantry_ingredient:
            return None
        await db.delete(pantry_ingredient)
        await db.commit()
        return pantry_ingredient

    @staticmethod
    async def get_pantry_ingredients_by_userid(db, userid):
        result = await db.execute(
            select(Pantry)
            .options(selectinload(Pantry.pantry_ingredients).selectinload(PantryIngredients.ingredient))
            .where(Pantry.userid == userid)
        )

        pantry = result.scalars().first()
        return pantry

    @staticmethod
    async def get_pantry_by_userid(db, userid):
        result = await db.execute(
            select(Pantry).where(Pantry.userid == userid)
        )

        pantry = result.scalars().all()
        print(pantry)
        return pantry
