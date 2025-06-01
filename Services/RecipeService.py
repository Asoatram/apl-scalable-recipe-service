import json
import re

from dotenv import load_dotenv
import os

from fastapi import HTTPException
from openai import OpenAI

from Repository.RecipeRepository import RecipeRepository
from Repository.PantryRepository import PantryRepository
from Core.kafka_producer import kafka_producer
from uuid import uuid4
import asyncio


load_dotenv()
client = OpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url=os.getenv("OPENAI_API_URL")
    )

pending_responses = {}
RESPONSE_TIMEOUT = 100


class RecipeService:
    @staticmethod
    async def get_recipe_from_id(db,id):
       return await RecipeRepository.get_recipe_details(db=db, recipe_id=id)
    @staticmethod
    async def get_recipe_paginated(db,page, per_page):
        return await RecipeRepository.get_recipe_pagination(db=db, page=page, per_page=per_page)
    @staticmethod
    async def post_recipe(db, recipe):
       return await RecipeRepository.create_recipe(db, recipe)

    @staticmethod
    async def delete_recipe(db, recipe_id):
        return await RecipeRepository.delete_recipe(db=db, recipe_id=recipe_id)

    @staticmethod
    async def save_recipe(db, user_id, recipe_id):
        return RecipeRepository.save_recipe(db=db, user_id=user_id, recipe_id=recipe_id)

    @staticmethod
    async def ask_for_tips(user_message):
        correlation_id = str(uuid4())
        payload = {
            "id": correlation_id,
            "question": user_message
        }
        future = asyncio.get_event_loop().create_future()
        pending_responses[correlation_id] = future
        await kafka_producer.send(topic=os.getenv("KAFKA_TOPIC"), value=payload)
        try:
            result = await asyncio.wait_for(future, timeout=RESPONSE_TIMEOUT)
            return {"response": result}
        except asyncio.TimeoutError:
            pending_responses.pop(correlation_id, None)
            raise HTTPException(status_code=504, detail="Timed out waiting for response")

    @staticmethod
    async def ask_for_recipe(db, user_id):
        correlation_id = str(uuid4())

        available_ingredients = ""
        ingredients_list = await PantryRepository.get_pantry_ingredients_by_userid(db, user_id)
        for ingredient in ingredients_list.pantry_ingredients:
            available_ingredients += f"{ingredient.ingredient.name}, "

        payload = {
            "id": correlation_id,
            "tutorial": available_ingredients
        }
        future = asyncio.get_event_loop().create_future()
        pending_responses[correlation_id] = future
        await kafka_producer.send(topic=os.getenv("KAFKA_TOPIC"), value=payload)
        try:
            result = await asyncio.wait_for(future, timeout=RESPONSE_TIMEOUT)
            return result
        except asyncio.TimeoutError:
            pending_responses.pop(correlation_id, None)
            raise HTTPException(status_code=504, detail="Timed out waiting for response")
        return result
