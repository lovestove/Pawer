"""
CRUD операции для работы с базой данных
"""
from sqlalchemy.orm import Session
from .models import User, Pet, Item, UserItem, PetSkill
from datetime import datetime, timedelta
import random


# === ПОЛЬЗОВАТЕЛИ ===

def get_or_create_user(db: Session, telegram_id: int, username: str = None, first_name: str = None):
    """Получить пользователя или создать нового"""
    user = db.query(User).filter(User.telegram_id == telegram_id).first()

    if not user:
        user = User(
            telegram_id=telegram_id,
            username=username,
            first_name=first_name,
            coins=100,
            crystals=10  # Стартовый бонус
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    else:
        # Обновляем last_active
        user.last_active = datetime.now()

        # Проверяем стрик логинов
        if user.last_login_date:
            days_diff = (datetime.now().date() - user.last_login_date.date()).days
            if days_diff == 1:
                user.login_streak += 1
            elif days_diff > 1:
                user.login_streak = 1

        user.last_login_date = datetime.now()
        db.commit()

    return user


def update_user_currency(db: Session, user_id: int, coins: int = 0, crystals: int = 0):
    """Обновить валюту пользователя"""
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.coins += coins
        user.crystals += crystals
        db.commit()
    return user


# === ПИТОМЦЫ ===

def create_pet(db: Session, owner_id: int, name: str, species: str, personality: str,
               color: str = 'blue', pattern: str = 'solid'):
    """Создать нового питомца"""
    pet = Pet(
        owner_id=owner_id,
        name=name,
        species=species,
        personality=personality,
        color=color,
        pattern=pattern,
        health=100,
        happiness=100,
        intelligence=50,
        energy=100
    )
    db.add(pet)
    db.commit()
    db.refresh(pet)
    return pet


def get_user_pets(db: Session, user_id: int):
    """Получить всех питомцев пользователя"""
    return db.query(Pet).filter(Pet.owner_id == user_id).all()


def get_pet_by_id(db: Session, pet_id: int):
    """Получить питомца по ID"""
    return db.query(Pet).filter(Pet.id == pet_id).first()


def update_pet_stats(db: Session, pet_id: int, **stats):
    """Обновить статы питомца

    Пример: update_pet_stats(db, pet_id, health=+10, happiness=+20)
    """
    pet = get_pet_by_id(db, pet_id)
    if not pet:
        return None

    # Обновляем статы и следим чтобы были в диапазоне 0-100
    if 'health' in stats:
        pet.health = max(0, min(100, pet.health + stats['health']))
    if 'happiness' in stats:
        pet.happiness = max(0, min(100, pet.happiness + stats['happiness']))
    if 'intelligence' in stats:
        pet.intelligence = max(0, min(100, pet.intelligence + stats['intelligence']))
    if 'energy' in stats:
        pet.energy = max(0, min(100, pet.energy + stats['energy']))

    db.commit()
    db.refresh(pet)
    return pet


def feed_pet(db: Session, pet_id: int, food_item: Item):
    """Покормить питомца"""
    pet = get_pet_by_id(db, pet_id)
    if not pet:
        return None

    # Применяем эффекты еды
    pet.health = min(100, pet.health + food_item.health_effect)
    pet.happiness = min(100, pet.happiness + food_item.happiness_effect)
    pet.energy = min(100, pet.energy + food_item.energy_effect)
    pet.intelligence = min(100, pet.intelligence + food_item.intelligence_effect)

    pet.last_fed = datetime.now()

    db.commit()
    db.refresh(pet)
    return pet


def add_pet_xp(db: Session, pet_id: int, xp_amount: int):
    """Добавить опыт питомцу и проверить повышение уровня"""
    pet = get_pet_by_id(db, pet_id)
    if not pet:
        return None

    pet.xp += xp_amount

    # Формула для levelup: нужно level * 100 XP для следующего уровня
    xp_needed = pet.level * 100

    leveled_up = False
    while pet.xp >= xp_needed:
        pet.xp -= xp_needed
        pet.level += 1
        leveled_up = True
        xp_needed = pet.level * 100

        # Проверяем эволюцию
        check_evolution(db, pet)

    db.commit()
    db.refresh(pet)

    return {'pet': pet, 'leveled_up': leveled_up}


def check_evolution(db: Session, pet: Pet):
    """Проверить и применить эволюцию"""
    evolution_levels = [5, 15, 30, 50, 75]

    if pet.level in evolution_levels:
        new_stage = evolution_levels.index(pet.level) + 1
        if new_stage > pet.evolution_stage:
            pet.evolution_stage = new_stage
            # Здесь можно добавить логику изменения внешнего вида

    db.commit()


def play_with_pet(db: Session, pet_id: int, game_type: str = 'simple'):
    """Играть с питомцем"""
    pet = get_pet_by_id(db, pet_id)
    if not pet:
        return None

    # Проверяем энергию
    if pet.energy < 10:
        return {'success': False, 'message': 'Питомец слишком устал! Дай ему отдохнуть 😴'}

    # Тратим энергию
    pet.energy = max(0, pet.energy - 10)

    # Повышаем счастье и даем XP
    pet.happiness = min(100, pet.happiness + 15)
    pet.total_games_played += 1
    pet.last_played = datetime.now()

    xp_gained = random.randint(20, 50)
    result = add_pet_xp(db, pet_id, xp_gained)

    db.commit()

    return {
        'success': True,
        'message': 'Отлично поиграли! 🎮',
        'xp_gained': xp_gained,
        'leveled_up': result['leveled_up']
    }


def rest_pet(db: Session, pet_id: int):
    """Дать питомцу отдохнуть"""
    pet = get_pet_by_id(db, pet_id)
    if not pet:
        return None

    # Восстанавливаем энергию
    pet.energy = min(100, pet.energy + 30)
    pet.last_sleep = datetime.now()

    db.commit()
    db.refresh(pet)
    return pet


# === ПРЕДМЕТЫ ===

def get_item_by_id(db: Session, item_id: int):
    """Получить предмет по ID"""
    return db.query(Item).filter(Item.id == item_id).first()


def get_all_items(db: Session, item_type: str = None):
    """Получить все предметы (опционально по типу)"""
    query = db.query(Item)
    if item_type:
        query = query.filter(Item.item_type == item_type)
    return query.all()


def add_item_to_user(db: Session, user_id: int, item_id: int, quantity: int = 1):
    """Добавить предмет в инвентарь пользователя"""
    # Проверяем, есть ли уже такой предмет
    user_item = db.query(UserItem).filter(
        UserItem.user_id == user_id,
        UserItem.item_id == item_id
    ).first()

    if user_item:
        user_item.quantity += quantity
    else:
        user_item = UserItem(
            user_id=user_id,
            item_id=item_id,
            quantity=quantity
        )
        db.add(user_item)

    db.commit()
    db.refresh(user_item)
    return user_item


def get_user_inventory(db: Session, user_id: int, item_type: str = None):
    """Получить инвентарь пользователя"""
    query = db.query(UserItem).filter(UserItem.user_id == user_id)

    if item_type:
        query = query.join(Item).filter(Item.item_type == item_type)

    return query.all()


def use_item(db: Session, user_id: int, item_id: int):
    """Использовать предмет из инвентаря"""
    user_item = db.query(UserItem).filter(
        UserItem.user_id == user_id,
        UserItem.item_id == item_id
    ).first()

    if not user_item or user_item.quantity <= 0:
        return {'success': False, 'message': 'У тебя нет этого предмета!'}

    # Уменьшаем количество
    user_item.quantity -= 1

    if user_item.quantity == 0:
        db.delete(user_item)

    db.commit()

    return {'success': True, 'item': user_item.item}


# === НАВЫКИ ===

def learn_skill(db: Session, pet_id: int, skill_name: str, skill_type: str):
    """Изучить новый навык"""
    # Проверяем, есть ли уже такой навык
    existing = db.query(PetSkill).filter(
        PetSkill.pet_id == pet_id,
        PetSkill.skill_name == skill_name
    ).first()

    if existing:
        return {'success': False, 'message': 'Питомец уже знает этот навык!'}

    skill = PetSkill(
        pet_id=pet_id,
        skill_name=skill_name,
        skill_type=skill_type
    )
    db.add(skill)
    db.commit()
    db.refresh(skill)

    return {'success': True, 'skill': skill}


def get_pet_skills(db: Session, pet_id: int):
    """Получить все навыки питомца"""
    return db.query(PetSkill).filter(PetSkill.pet_id == pet_id).all()


# === АВТООБНОВЛЕНИЕ СТАТОВ ===

def auto_update_pet_stats(db: Session):
    """
    Автоматическое снижение статов со временем
    Запускать эту функцию периодически (например, каждый час)
    """
    all_pets = db.query(Pet).all()

    for pet in all_pets:
        now = datetime.now()

        # Снижение здоровья (если не кормили > 4 часов)
        if (now - pet.last_fed).seconds > 14400:  # 4 часа
            pet.health = max(5, pet.health - 5)  # Не опускаем до 0, минимум 5

        # Снижение счастья (если не играли > 6 часов)
        if (now - pet.last_played).seconds > 21600:  # 6 часов
            pet.happiness = max(5, pet.happiness - 5)

        # Снижение энергии (всегда, если не спал > 3 часов)
        if (now - pet.last_sleep).seconds > 10800:  # 3 часа
            pet.energy = max(0, pet.energy - 3)

    db.commit()