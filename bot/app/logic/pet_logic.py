from datetime import datetime, timedelta

from ..core.database import Database

# Constants for interactions
FEED_VALUE = 25
WATER_VALUE = 25
PLAY_VALUE = 20

# Constants for stat decay
HUNGER_DECAY_RATE = 2  # points per hour
THIRST_DECAY_RATE = 3  # points per hour
HAPPINESS_DECAY_RATE = 1  # points per hour


async def calculate_and_update_pet_stats(user_id: int, db: Database) -> dict | None:
    """
    Calculates the pet's current stats based on decay over time and updates the database.

    Args:
        user_id: The user's Telegram ID.
        db: The database instance.

    Returns:
        The updated pet data as a dictionary, or None if no pet is found.
    """
    pet = await db.get_pet(user_id)
    if not pet:
        return None

    now = datetime.now()
    last_updated = datetime.fromisoformat(pet["last_updated"])
    hours_passed = (now - last_updated).total_seconds() / 3600

    # Calculate new stat values
    hunger = max(0, pet["hunger"] - hours_passed * HUNGER_DECAY_RATE)
    thirst = max(0, pet["thirst"] - hours_passed * THIRST_DECAY_RATE)
    happiness = max(0, pet["happiness"] - hours_passed * HAPPINESS_DECAY_RATE)

    # Update the database with the new decayed stats
    await db.update_pet_stats(user_id, int(hunger), int(thirst), int(happiness))

    # Fetch the updated pet data to return it
    updated_pet = await db.get_pet(user_id)
    return updated_pet
