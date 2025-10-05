"""
Модели базы данных для Digital Pet
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class User(Base):
    """Пользователь бота"""
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, nullable=False)
    username = Column(String(255))
    first_name = Column(String(255))

    # Валюта
    coins = Column(Integer, default=100)  # Игровая валюта
    crystals = Column(Integer, default=0)  # Донатная валюта

    # Premium
    is_premium = Column(Boolean, default=False)
    premium_until = Column(DateTime, nullable=True)

    # Статистика
    created_at = Column(DateTime, default=datetime.now)
    last_active = Column(DateTime, default=datetime.now)
    login_streak = Column(Integer, default=0)
    last_login_date = Column(DateTime, default=datetime.now)

    # Связи
    pets = relationship('Pet', back_populates='owner', cascade='all, delete-orphan')
    items = relationship('UserItem', back_populates='user', cascade='all, delete-orphan')


class Pet(Base):
    """Питомец пользователя"""
    __tablename__ = 'pets'

    id = Column(Integer, primary_key=True)
    owner_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    # Основные данные
    name = Column(String(100), nullable=False)
    species = Column(String(50), nullable=False)  # Вид: dragon, cyber_cat, cloud, etc.
    personality = Column(String(50), nullable=False)  # Характер: playful, lazy, smart, etc.

    # Внешний вид
    color = Column(String(50), default='blue')
    pattern = Column(String(50), default='solid')
    image_url = Column(String(500), nullable=True)

    # Статы (0-100)
    health = Column(Float, default=100.0)
    happiness = Column(Float, default=100.0)
    intelligence = Column(Float, default=50.0)
    energy = Column(Float, default=100.0)

    # Прогресс
    level = Column(Integer, default=1)
    xp = Column(Integer, default=0)
    evolution_stage = Column(Integer, default=0)  # 0-4 (малыш -> легенда)
    evolution_path = Column(String(50), default='neutral')  # battle, cute, dark, smart

    # Время
    created_at = Column(DateTime, default=datetime.now)
    last_fed = Column(DateTime, default=datetime.now)
    last_played = Column(DateTime, default=datetime.now)
    last_sleep = Column(DateTime, default=datetime.now)

    # Статистика
    total_games_played = Column(Integer, default=0)
    battles_won = Column(Integer, default=0)
    battles_lost = Column(Integer, default=0)

    # Связи
    owner = relationship('User', back_populates='pets')
    skills = relationship('PetSkill', back_populates='pet', cascade='all, delete-orphan')
    equipment = relationship('PetEquipment', back_populates='pet', cascade='all, delete-orphan')


class PetSkill(Base):
    """Навыки питомца"""
    __tablename__ = 'pet_skills'

    id = Column(Integer, primary_key=True)
    pet_id = Column(Integer, ForeignKey('pets.id'), nullable=False)

    skill_name = Column(String(100), nullable=False)
    skill_type = Column(String(50))  # battle, social, creative
    level = Column(Integer, default=1)

    learned_at = Column(DateTime, default=datetime.now)

    pet = relationship('Pet', back_populates='skills')


class Item(Base):
    """Предметы в игре (еда, экипировка, косметика)"""
    __tablename__ = 'items'

    id = Column(Integer, primary_key=True)

    name = Column(String(100), nullable=False)
    description = Column(Text)
    item_type = Column(String(50), nullable=False)  # food, equipment, cosmetic
    rarity = Column(String(50), default='common')  # common, rare, epic, legendary

    # Эффекты
    health_effect = Column(Float, default=0)
    happiness_effect = Column(Float, default=0)
    intelligence_effect = Column(Float, default=0)
    energy_effect = Column(Float, default=0)

    # Для экипировки
    stat_bonus = Column(String(200))  # JSON строка с бонусами

    # Цена
    coin_price = Column(Integer, default=0)
    crystal_price = Column(Integer, default=0)

    # Визуал
    icon_emoji = Column(String(10), default='📦')
    image_url = Column(String(500), nullable=True)


class UserItem(Base):
    """Предметы пользователя (инвентарь)"""
    __tablename__ = 'user_items'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    item_id = Column(Integer, ForeignKey('items.id'), nullable=False)

    quantity = Column(Integer, default=1)
    obtained_at = Column(DateTime, default=datetime.now)

    user = relationship('User', back_populates='items')
    item = relationship('Item')


class PetEquipment(Base):
    """Экипированные предметы на питомце"""
    __tablename__ = 'pet_equipment'

    id = Column(Integer, primary_key=True)
    pet_id = Column(Integer, ForeignKey('pets.id'), nullable=False)
    item_id = Column(Integer, ForeignKey('items.id'), nullable=False)

    slot = Column(String(50))  # weapon, armor, accessory
    equipped_at = Column(DateTime, default=datetime.now)

    pet = relationship('Pet', back_populates='equipment')
    item = relationship('Item')


class Quest(Base):
    """Ежедневные квесты"""
    __tablename__ = 'quests'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    quest_type = Column(String(50), nullable=False)  # feed_3_times, win_battle, etc.
    progress = Column(Integer, default=0)
    target = Column(Integer, nullable=False)

    completed = Column(Boolean, default=False)
    reward_coins = Column(Integer, default=50)
    reward_xp = Column(Integer, default=100)

    created_at = Column(DateTime, default=datetime.now)
    completed_at = Column(DateTime, nullable=True)