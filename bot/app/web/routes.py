import hmac
import hashlib
import json
from typing import Union, Tuple
from urllib.parse import parse_qsl

from aiohttp import web

from app.core import Database, settings
from app.handlers.pet import calculate_and_update_pet_stats, FEED_VALUE, WATER_VALUE, PLAY_VALUE


def validate_init_data(init_data: str, bot_token: str) -> Tuple[bool, Union[dict, None]]:
    """
    Validates the initData received from the Telegram Mini App.

    Args:
        init_data: The raw initData string.
        bot_token: The bot's API token.

    Returns:
        A tuple containing a boolean indicating if the data is valid,
        and a dictionary with the parsed user data if valid.
    """
    try:
        parsed_data = dict(parse_qsl(init_data))
    except ValueError:
        return False, None

    if "hash" not in parsed_data:
        return False, None

    hash_from_telegram = parsed_data.pop("hash")
    data_check_string = "\n".join(
        f"{key}={value}" for key, value in sorted(parsed_data.items())
    )

    secret_key = hmac.new("WebAppData".encode(), bot_token.encode(), hashlib.sha256).digest()
    calculated_hash = hmac.new(
        secret_key, data_check_string.encode(), hashlib.sha256
    ).hexdigest()

    if calculated_hash == hash_from_telegram:
        try:
            user_data = json.loads(parsed_data.get("user", "{}"))
            if "id" in user_data:
                return True, user_data
        except json.JSONDecodeError:
            return False, None

    return False, None


async def get_pet_data(request: web.Request):
    """Handler to get pet data."""
    db: Database = request.app["db"]
    init_data = request.headers.get("Authorization", "").split(" ")[-1]

    is_valid, user_data = validate_init_data(init_data, settings.BOT_TOKEN)
    if not is_valid or not user_data:
        return web.HTTPUnauthorized(text="Invalid initData")

    user_id = user_data["id"]
    pet = await calculate_and_update_pet_stats(user_id, db)

    if not pet:
        return web.HTTPNotFound(text="Pet not found")

    return web.json_response(pet)


async def interact_with_pet(request: web.Request):
    """Handler for pet interactions."""
    db: Database = request.app["db"]
    init_data = request.headers.get("Authorization", "").split(" ")[-1]

    is_valid, user_data = validate_init_data(init_data, settings.BOT_TOKEN)
    if not is_valid or not user_data:
        return web.HTTPUnauthorized(text="Invalid initData")

    try:
        data = await request.json()
        action = data.get("action")
    except json.JSONDecodeError:
        return web.HTTPBadRequest(text="Invalid JSON")

    if not action:
        return web.HTTPBadRequest(text="Action not specified")

    user_id = user_data["id"]
    pet = await calculate_and_update_pet_stats(user_id, db)
    if not pet:
        return web.HTTPNotFound(text="Pet not found")

    hunger, thirst, happiness = pet["hunger"], pet["thirst"], pet["happiness"]

    if action == "feed":
        hunger = min(100, hunger + FEED_VALUE)
        happiness = min(100, happiness + 5)
    elif action == "water":
        thirst = min(100, thirst + WATER_VALUE)
        happiness = min(100, happiness + 5)
    elif action == "play":
        happiness = min(100, happiness + PLAY_VALUE)
        hunger = max(0, hunger - 5)
        thirst = max(0, thirst - 7)
    else:
        return web.HTTPBadRequest(text="Invalid action")

    await db.update_pet_stats(user_id, hunger, thirst, happiness)
    updated_pet = await db.get_pet(user_id)

    return web.json_response(updated_pet)