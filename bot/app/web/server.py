from aiohttp import web
import json
import hashlib
import hmac
from urllib.parse import unquote, parse_qs
from pathlib import Path
from ..core.database import db
from ..core.config import settings, GameConfig


def verify_telegram_web_app_data(init_data: str, bot_token: str) -> dict:
    """Проверка данных от Telegram Web App"""
    try:
        parsed_data = parse_qs(init_data)

        # Извлекаем hash
        received_hash = parsed_data.get('hash', [''])[0]

        # Создаем data_check_string
        data_check_arr = []
        for key, value in parsed_data.items():
            if key != 'hash':
                data_check_arr.append(f"{key}={value[0]}")

        data_check_arr.sort()
        data_check_string = '\n'.join(data_check_arr)

        # Вычисляем hash
        secret_key = hmac.new(
            "WebAppData".encode(),
            bot_token.encode(),
            hashlib.sha256
        ).digest()

        calculated_hash = hmac.new(
            secret_key,
            data_check_string.encode(),
            hashlib.sha256
        ).hexdigest()

        if calculated_hash != received_hash:
            return None

        # Извлекаем user данные
        user_json = parsed_data.get('user', ['{}'])[0]
        user_data = json.loads(unquote(user_json))

        return user_data

    except Exception as e:
        print(f"Ошибка проверки: {e}")
        return None


async def handle_static(request):
    """Обработка статических файлов"""
    filename = request.match_info.get('filename', 'index.html')

    # Защита от path traversal
    if '..' in filename or filename.startswith('/'):
        return web.Response(status=403)

    static_dir = Path(__file__).parent.parent.parent.parent / 'mini_app'
    file_path = static_dir / filename

    if not file_path.exists():
        return web.Response(status=404)

    # Определение MIME типа
    mime_types = {
        '.html': 'text/html',
        '.css': 'text/css',
        '.js': 'application/javascript',
        '.json': 'application/json',
        '.png': 'image/png',
        '.jpg': 'image/jpeg',
        '.gif': 'image/gif',
        '.svg': 'image/svg+xml'
    }

    mime_type = mime_types.get(file_path.suffix, 'text/plain')

    return web.FileResponse(file_path, headers={'Content-Type': mime_type})


async def handle_get_pet(request):
    """Получение данных о питомце"""
    # Проверка авторизации
    auth_header = request.headers.get('Authorization', '')

    if not auth_header.startswith('tma '):
        return web.json_response({'error': 'Unauthorized'}, status=401)

    init_data = auth_header[4:]
    user_data = verify_telegram_web_app_data(init_data, settings.BOT_TOKEN)

    if not user_data:
        return web.json_response({'error': 'Invalid auth'}, status=401)

    user_id = user_data['id']

    # Получение данных
    user = await db.get_user(user_id)
    pet = await db.get_active_pet(user_id)
    inventory = await db.get_inventory(user_id)

    if not pet:
        return web.json_response({'error': 'No pet'}, status=404)

    # Формирование ответа
    pet_type_info = GameConfig.PET_TYPES.get(pet['pet_type'], {})

    return web.json_response({
        'user': {
            'coins': user['coins'],
            'gems': user['gems'],
            'streak_days': user['streak_days']
        },
        'pet': {
            'name': pet['name'],
            'type': pet['pet_type'],
            'emoji': pet_type_info.get('emoji', '🐱'),
            'level': pet['level'],
            'exp': pet['exp'],
            'hunger': pet['hunger'],
            'happiness': pet['happiness'],
            'energy': pet['energy'],
            'hygiene': pet['hygiene']
        },
        'inventory': inventory
    })


async def handle_use_item(request):
    """Использование предмета"""
    # Проверка авторизации
    auth_header = request.headers.get('Authorization', '')

    if not auth_header.startswith('tma '):
        return web.json_response({'error': 'Unauthorized'}, status=401)

    init_data = auth_header[4:]
    user_data = verify_telegram_web_app_data(init_data, settings.BOT_TOKEN)

    if not user_data:
        return web.json_response({'error': 'Invalid auth'}, status=401)

    user_id = user_data['id']

    # Получение данных запроса
    try:
        data = await request.json()
        item_id = data.get('item_id')
    except:
        return web.json_response({'error': 'Invalid request'}, status=400)

    if item_id not in GameConfig.SHOP_ITEMS:
        return web.json_response({'error': 'Item not found'}, status=404)

    # Проверка наличия предмета
    quantity = await db.get_item_quantity(user_id, item_id)
    if quantity <= 0:
        return web.json_response({'error': 'Item not in inventory'}, status=400)

    # Проверка наличия питомца
    pet = await db.get_active_pet(user_id)
    if not pet:
        return web.json_response({'error': 'No pet'}, status=404)

    item = GameConfig.SHOP_ITEMS[item_id]

    # Применение эффектов
    if item.get('hunger_restore'):
        new_hunger = min(100, pet['hunger'] + item['hunger_restore'])
        await db.update_pet_stat(pet['id'], 'hunger', new_hunger)

    if item.get('happiness_restore'):
        new_happiness = min(100, pet['happiness'] + item['happiness_restore'])
        await db.update_pet_stat(pet['id'], 'happiness', new_happiness)

    if item.get('energy_restore'):
        new_energy = min(100, pet['energy'] + item['energy_restore'])
        await db.update_pet_stat(pet['id'], 'energy', new_energy)

    if item.get('hygiene_restore'):
        new_hygiene = min(100, pet['hygiene'] + item['hygiene_restore'])
        await db.update_pet_stat(pet['id'], 'hygiene', new_hygiene)

    if item.get('energy_cost'):
        new_energy = max(0, pet['energy'] - item['energy_cost'])
        await db.update_pet_stat(pet['id'], 'energy', new_energy)

    # Добавление опыта
    exp_gain = 10
    level_up = await db.add_exp(pet['id'], exp_gain)

    # Удаление предмета
    await db.remove_item(user_id, item_id, 1)

    # Обновленные данные
    pet = await db.get_active_pet(user_id)
    inventory = await db.get_inventory(user_id)
    pet_type_info = GameConfig.PET_TYPES.get(pet['pet_type'], {})

    return web.json_response({
        'success': True,
        'level_up': level_up,
        'pet': {
            'name': pet['name'],
            'type': pet['pet_type'],
            'emoji': pet_type_info.get('emoji', '🐱'),
            'level': pet['level'],
            'exp': pet['exp'],
            'hunger': pet['hunger'],
            'happiness': pet['happiness'],
            'energy': pet['energy'],
            'hygiene': pet['hygiene']
        },
        'inventory': inventory
    })


async def init_web_app(app):
    """Инициализация веб-приложения"""
    app.router.add_get('/', handle_static)
    app.router.add_get('/{filename}', handle_static)
    app.router.add_get('/api/pet', handle_get_pet)
    app.router.add_post('/api/use_item', handle_use_item)


def create_app():
    """Создание приложения"""
    app = web.Application()
    app.on_startup.append(init_web_app)
    return app