import os
import logging
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# ✅ ПРАВИЛЬНОЕ ПОЛУЧЕНИЕ ТОКЕНА
def get_bot_token():
    # Пробуем получить из переменных окружения
    token_from_env = os.environ.get("BOT_TOKEN")
    
    if token_from_env and token_from_env.strip() and token_from_env != "8268375064:AAE7Lujf07p6YiCV1lVrnIB1E8D_mzQOa2Q":
        logging.info("✅ Используется токен из переменных окружения")
        return token_from_env
    else:
        # Используем дефолтный токен
        logging.warning("⚠️ Используется дефолтный токен. Для продакшена добавьте BOT_TOKEN в переменные окружения!")
        return "8268375064:AAE7Lujf07p6YiCV1lVrnIB1E8D_mzQOa2Q"

BOT_TOKEN = get_bot_token()
CREATOR = "StarField"
CODER = "dewlops"

# Хранилище данных
games = {}
challenges = {}
user_data = {}
player_games = {}

# Списки фраз для сбива прицела
AIM_DISRUPT_PHRASES = [
    "произнося древнее заклинание",
    "используя технику ниндзя",
    "с помощью гипноза",
    "используя силу мысли",
    "произнося мантру",
    "с помощью телекинеза",
    "используя магический артефакт",
    "произнося магическое заклинание",
    "с помощью техники дыхания",
    "используя боевой клич"
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Главное меню с информацией"""
    keyboard = [
        [InlineKeyboardButton("🎮 Начать дуэль с ботом", callback_data="battle_bot")],
        [InlineKeyboardButton("⚔️ Вызвать игрока на дуэль", callback_data="challenge_info")],
        [InlineKeyboardButton("📊 Статистика", callback_data="stats")],
        [InlineKeyboardButton("👥 Добавить в группу", url=f"https://t.me/{(await context.bot.get_me()).username}?startgroup=true")],
        [InlineKeyboardButton("ℹ️ О создателях", callback_data="about_creators")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = (
        "🎯 *Добро пожаловать в Knife Duel Bot!*\n\n"
        "⚔️ *Новые возможности:*\n"
        "• Дуэли с ботом\n"
        "• PvP сражения с другими игроками\n"
        "• Система вызовов через ответ на сообщения\n"
        "• *Новое!* Сбив прицела противника\n"
        "• *Новое!* Уведомления в чате о результатах\n\n"
        "🎮 *Как играть:*\n"
        "• 🎯 Прицеливание - +25% к шансу (передает ход)\n"
        "• 🔪 Бросок - атака противника (передает ход)\n"
        "• 🌀 Сбив прицела - обнуляет прицел противника (передает ход)\n"
        "• Максимальный шанс попадания: 75%\n"
        "• Прицеливание суммируется до броска!"
    )
    
    if update.message:
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode='Markdown')
    else:
        await update.callback_query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

async def about_creators(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Информация о создателях"""
    query = update.callback_query
    await query.answer()
    
    text = (
        "👨‍💻 *Информация о создателях:*\n\n"
        f"💡 *Идея и концепция:* {CREATOR}\n"
        f"⚙️ *Разработка и код:* {CODER}\n\n"
        "🎯 *Knife Duel Bot* - телеграм бот для увлекательных дуэлей в метании ножей!\n\n"
        "📧 *Для связи:* @starfieldx"
    )
    
    keyboard = [[InlineKeyboardButton("⬅️ Назад в меню", callback_data="main_menu")]]
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

async def challenge_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Информация о вызовах"""
    query = update.callback_query
    await query.answer()
    
    text = (
        "⚔️ *Система вызовов на дуэль:*\n\n"
        "📝 *Как вызвать игрока:*\n"
        "1. Найти сообщение игрока в чате\n"
        "2. Ответить на него командой: *Сразить* или *Дуэль*\n"
        "3. Ожидать принятия вызова\n\n"
        "🎯 *Игрок получит:*\n"
        "• Уведомление о вызове\n" 
        "• Кнопки Принять/Отклонить\n"
        "• 60 секунд на ответ"
    )
    
    keyboard = [
        [InlineKeyboardButton("🎮 Дуэль с ботом", callback_data="battle_bot")],
        [InlineKeyboardButton("⬅️ Назад в меню", callback_data="main_menu")]
    ]
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

async def battle_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начало игры с ботом"""
    query = update.callback_query
    user_id = query.from_user.id
    
    # Инициализация игры с ботом
    game_id = f"pve_{user_id}"
    games[game_id] = {
        'aim': 0,
        'hp': 100,
        'enemy_hp': 100,
        'mode': 'pve',
        'player_id': user_id
    }
    player_games[user_id] = game_id
    
    await query.answer()
    await query.edit_message_text(
        text=f"🤖 *Дуэль с ботом!*\n\n❤️ Ваше HP: 100\n💀 Бот HP: 100\n🎯 Шанс попадания: 25%",
        reply_markup=game_keyboard_pve(),
        parse_mode='Markdown'
    )

async def handle_all_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка ВСЕХ сообщений для вызовов"""
    if not update.message or not update.message.reply_to_message:
        return
    
    # Проверяем текст сообщения
    message_text = update.message.text.lower().strip() if update.message.text else ""
    
    # Список команд для вызова
    challenge_commands = ["сразить", "дуэль", "вызов", "вызвать", "бой", "поединок"]
    
    if message_text in challenge_commands:
        await create_challenge(update, context)

async def create_challenge(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Создание вызова через ответ на сообщение"""
    try:
        challenger = update.message.from_user
        target_message = update.message.reply_to_message
        target_user = target_message.from_user
        
        # Логируем информацию для отладки
        logging.info(f"Вызов от {challenger.id} ({challenger.first_name}) для {target_user.id} ({target_user.first_name})")
        
        # Проверки
        if challenger.id == target_user.id:
            await update.message.reply_text(
                "❌ Нельзя вызвать самого себя на дуэль!",
                reply_to_message_id=update.message.message_id
            )
            return
        
        if challenger.id in challenges:
            await update.message.reply_text(
                "❌ У вас уже есть активный вызов!",
                reply_to_message_id=update.message.message_id
            )
            return
        
        # Сохраняем вызов
        challenges[challenger.id] = {
            'target_id': target_user.id,
            'challenger_name': challenger.first_name,
            'target_name': target_user.first_name,
            'chat_id': update.message.chat_id,
            'message_id': update.message.message_id,
            'timestamp': update.message.date.timestamp()
        }
        
        user_data[challenger.id] = challenger.first_name
        user_data[target_user.id] = target_user.first_name
        
        # Клавиатура для принятия вызова
        keyboard = [
            [
                InlineKeyboardButton("✅ Принять вызов", callback_data=f"accept_{challenger.id}"),
                InlineKeyboardButton("❌ Отклонить", callback_data=f"decline_{challenger.id}")
            ]
        ]
        
        challenge_text = (
            f"⚔️ *ВЫЗОВ НА ДУЭЛЬ!*\n\n"
            f"🎯 *{challenger.first_name}* вызывает вас на бой!\n"
            f"💬 Из чата: {update.message.chat.title if update.message.chat.title else 'личные сообщения'}\n"
            f"⏰ У вас 60 секунд чтобы принять вызов"
        )
        
        # Отправляем вызов в ЛС
        try:
            await context.bot.send_message(
                chat_id=target_user.id,
                text=challenge_text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='Markdown'
            )
            
            # Уведомляем в чате
            await update.message.reply_text(
                f"🎯 *{challenger.first_name}* вызвал на дуэль *{target_user.first_name}*! "
                f"Ожидайте ответа...",
                reply_to_message_id=update.message.message_id,
                parse_mode='Markdown'
            )
            
            logging.info(f"Вызов успешно отправлен игроку {target_user.id}")
            
        except Exception as e:
            logging.error(f"Ошибка отправки вызова: {e}")
            await update.message.reply_text(
                f"❌ Не удалось отправить вызов *{target_user.first_name}*. "
                f"Возможно, игрок не запускал бота через /start",
                reply_to_message_id=update.message.message_id,
                parse_mode='Markdown'
            )
            if challenger.id in challenges:
                del challenges[challenger.id]
                
    except Exception as e:
        logging.error(f"Общая ошибка в create_challenge: {e}")
        await update.message.reply_text(
            "❌ Произошла ошибка при создании вызова",
            reply_to_message_id=update.message.message_id
        )

async def handle_challenge_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка ответа на вызов"""
    query = update.callback_query
    user_id = query.from_user.id
    data = query.data
    
    try:
        if data.startswith('accept_'):
            challenger_id = int(data.split('_')[1])
            
            if challenger_id in challenges:
                # Проверяем не устарел ли вызов (больше 60 секунд)
                challenge_data = challenges[challenger_id]
                current_time = update.callback_query.message.date.timestamp()
                if current_time - challenge_data['timestamp'] > 60:
                    await query.answer("❌ Время для принятия вызова истекло!", show_alert=True)
                    del challenges[challenger_id]
                    await query.message.edit_text("⏰ Время для принятия вызова истекло!")
                    return
                
                # Создаем игру PvP
                await start_pvp_game(query, context, challenger_id, user_id)
            else:
                await query.answer("❌ Вызов не найден или устарел!", show_alert=True)
        
        elif data.startswith('decline_'):
            challenger_id = int(data.split('_')[1])
            
            if challenger_id in challenges:
                challenge_data = challenges[challenger_id]
                challenger_name = challenge_data['challenger_name']
                
                # Уведомляем вызывающего
                try:
                    await context.bot.send_message(
                        chat_id=challenger_id,
                        text=f"❌ {query.from_user.first_name} отклонил ваш вызов на дуэль!"
                    )
                    
                    # Уведомляем в группе если вызов был из группы
                    if challenge_data['chat_id'] != query.message.chat_id:  # Если вызов из другого чата
                        await context.bot.send_message(
                            chat_id=challenge_data['chat_id'],
                            text=f"❌ {query.from_user.first_name} отклонил вызов на дуэль от {challenger_name}!",
                            reply_to_message_id=challenge_data.get('message_id')
                        )
                except Exception as e:
                    logging.error(f"Ошибка уведомления: {e}")
                
                # Очищаем вызов
                del challenges[challenger_id]
                await query.message.edit_text(f"❌ Вы отклонили вызов от {challenger_name}!")
            else:
                await query.answer("❌ Вызов не найден!", show_alert=True)
    
    except Exception as e:
        logging.error(f"Ошибка в handle_challenge_response: {e}")
        await query.answer("❌ Произошла ошибка!", show_alert=True)
    
    await query.answer()

async def start_pvp_game(query: Update, context: ContextTypes.DEFAULT_TYPE, player1_id: int, player2_id: int):
    """Начало PvP игры"""
    try:
        game_id = f"pvp_{player1_id}_{player2_id}"
        
        # Создаем игру
        games[game_id] = {
            'players': {
                player1_id: {'hp': 100, 'aim': 0, 'name': user_data.get(player1_id, "Игрок 1")},
                player2_id: {'hp': 100, 'aim': 0, 'name': user_data.get(player2_id, "Игрок 2")}
            },
            'current_turn': player1_id,
            'mode': 'pvp',
            'original_chat_id': challenges[player1_id]['chat_id'] if player1_id in challenges else None
        }
        
        # Сохраняем связь игроков с игрой
        player_games[player1_id] = game_id
        player_games[player2_id] = game_id
        
        # Очищаем вызов
        if player1_id in challenges:
            del challenges[player1_id]
        
        player1_name = user_data.get(player1_id, "Игрок 1")
        player2_name = user_data.get(player2_id, "Игрок 2")
        
        game_text = (
            f"⚔️ *ДУЭЛЬ НАЧАЛАСЬ!*\n\n"
            f"🔪 {player1_name} vs 🔪 {player2_name}\n\n"
            f"*Ход:* {player1_name}\n"
            f"❤️ HP: 100 | ❤️ HP: 100\n\n"
            f"💡 *Стратегия:* Прицеливание передает ход, но эффект сохраняется до броска!"
        )
        
        # Отправляем сообщения обоим игрокам
        await context.bot.send_message(
            chat_id=player1_id,
            text=game_text,
            reply_markup=game_keyboard_pvp(game_id, player1_id),
            parse_mode='Markdown'
        )
        
        await context.bot.send_message(
            chat_id=player2_id,
            text=game_text,
            reply_markup=game_keyboard_pvp(game_id, player2_id, is_current_turn=False),
            parse_mode='Markdown'
        )
        
        await query.message.edit_text("🎯 Дуэль началась! Проверьте личные сообщения с ботом.")
        
        # Уведомляем в исходном чате если это был групповой вызов
        original_chat_id = games[game_id]['original_chat_id']
        if original_chat_id:
            try:
                await context.bot.send_message(
                    chat_id=original_chat_id,
                    text=f"🎯 Дуэль между *{player1_name}* и *{player2_name}* началась!",
                    parse_mode='Markdown'
                )
            except:
                pass
                
    except Exception as e:
        logging.error(f"Ошибка начала PvP игры: {e}")
        await query.message.edit_text("❌ Ошибка начала дуэли. Убедитесь, что оба игрока запустили бота.")

async def handle_game_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик игровых действий"""
    query = update.callback_query
    user_id = query.from_user.id
    data = query.data
    
    logging.info(f"Обработка действия: {data} от пользователя {user_id}")
    
    try:
        if data.startswith('pvp_'):
            await handle_pvp_action(update, context)
        elif data in ['aim', 'throw', 'disrupt']:
            await handle_pve_action(update, context)
        else:
            await query.answer("❌ Неизвестное действие!")
    except Exception as e:
        logging.error(f"Ошибка в handle_game_action: {e}")
        await query.answer("❌ Произошла ошибка!", show_alert=True)

async def handle_pve_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик PvE действий"""
    query = update.callback_query
    user_id = query.from_user.id
    action = query.data
    
    # Ищем игру по user_id (для PvE)
    game_id = player_games.get(user_id)
    if not game_id or game_id not in games:
        await query.answer("❌ Игра не найдена! Начните новую игру.")
        return
    
    game = games[game_id]
    if game.get('mode') != 'pve':
        await query.answer("❌ Это не PvE игра!")
        return
    
    message = ""
    
    if action == "aim":
        game['aim'] = min(2, game['aim'] + 1)
        aim_bonus = game['aim'] * 25
        message = f"🎯 Вы прицелились! Шанс: {25 + aim_bonus}%"
    
    elif action == "disrupt":
        # В PvE сбив прицела не имеет смысла, так как бот не прицеливается
        message = "🤖 Бот не использует прицеливание!"
    
    elif action == "throw":
        hit_chance = 25 + (game['aim'] * 25)
        is_hit = random.randint(1, 100) <= hit_chance
        
        if is_hit:
            damage = random.randint(15, 25)
            game['enemy_hp'] -= damage
            message = f"✅ Попадание! Урон: {damage}"
        else:
            message = "❌ Промах!"
        
        game['aim'] = 0  # Сбрасываем прицел после броска
        
        # Ход бота
        if game['enemy_hp'] > 0:
            enemy_damage = random.randint(10, 20)
            game['hp'] -= enemy_damage
            message += f"\n🤖 Бот атакует! Урон: {enemy_damage}"
    
    # Проверка конца игры
    if game['hp'] <= 0 or game['enemy_hp'] <= 0:
        if game['hp'] <= 0:
            result = "💀 ВЫ ПРОИГРАЛИ!"
            winner = "БОТ"
            loser = "ВЫ"
        else:
            result = "🎉 ВЫ ПОБЕДИЛИ!"
            winner = "ВЫ"
            loser = "БОТ"
        
        message += f"\n\n{result}\n🏆 ПОБЕДИТЕЛЬ: {winner}\n💀 ПРОИГРАВШИЙ: {loser}\n\n⚡ by {CREATOR}"
        
        # Очищаем игру
        if game_id in games:
            del games[game_id]
        if user_id in player_games:
            del player_games[user_id]
            
        await query.edit_message_text(text=message)
        return
    
    # Обновление интерфейса
    aim_bonus = game['aim'] * 25
    await query.edit_message_text(
        text=f"🤖 *Дуэль с ботом:*\n❤️ Ваше HP: {game['hp']}\n💀 Бот HP: {game['enemy_hp']}\n🎯 Шанс: {25 + aim_bonus}%\n\n{message}",
        reply_markup=game_keyboard_pve(),
        parse_mode='Markdown'
    )
    
    await query.answer()

async def handle_pvp_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик PvP действий с НОВОЙ системой прицеливания"""
    query = update.callback_query
    user_id = query.from_user.id
    data = query.data
    
    logging.info(f"PvP действие: {data} от пользователя {user_id}")
    
    # Извлекаем game_id из callback_data
    parts = data.split('_')
    if len(parts) < 3:
        await query.answer("❌ Ошибка в данных!")
        return
        
    action = parts[1]
    game_id = f"pvp_{parts[2]}_{parts[3]}" if len(parts) >= 4 else None
    
    if not game_id:
        await query.answer("❌ Неверный формат game_id!")
        return
    
    # Ищем игру
    if game_id not in games:
        await query.answer("❌ Игра не найдена!")
        return
    
    game = games[game_id]
    players = game['players']
    
    # Проверяем, чей сейчас ход
    if user_id != game['current_turn']:
        await query.answer("❌ Сейчас не ваш ход!")
        return
    
    current_player = user_id
    opponent_id = [pid for pid in players.keys() if pid != current_player][0]
    
    message = ""
    
    if action == "aim":
        # Прицеливание - увеличиваем прицел и передаем ход
        players[current_player]['aim'] = min(2, players[current_player]['aim'] + 1)
        aim_bonus = players[current_player]['aim'] * 25
        message = f"🎯 {players[current_player]['name']} прицелился! Текущий шанс: {25 + aim_bonus}%\n\n"
        message += f"💡 Эффект прицеливания сохранится до вашего следующего броска!"
        
        # Прицеливание ВСЕГДА передает ход
        game['current_turn'] = opponent_id
    
    elif action == "disrupt":
        if players[opponent_id]['aim'] > 0:
            # Сбиваем прицел противника
            old_aim = players[opponent_id]['aim']
            players[opponent_id]['aim'] = 0
            disrupt_phrase = random.choice(AIM_DISRUPT_PHRASES)
            message = f"🌀 {players[current_player]['name']} сбил прицел {players[opponent_id]['name']}, {disrupt_phrase}!"
        else:
            message = f"🌀 {players[opponent_id]['name']} не прицеливался!"
        # Сбив прицела передает ход
        game['current_turn'] = opponent_id
    
    elif action == "throw":
        # Бросок ножа - используем накопленный прицел
        hit_chance = 25 + (players[current_player]['aim'] * 25)
        is_hit = random.randint(1, 100) <= hit_chance
        
        if is_hit:
            damage = random.randint(15, 25)
            players[opponent_id]['hp'] -= damage
            message = f"✅ {players[current_player]['name']} попал! Урон: {damage}"
            
            # Показываем эффект прицеливания если был
            if players[current_player]['aim'] > 0:
                message += f"\n💫 Эффект прицеливания (+{players[current_player]['aim'] * 25}%) помог!"
        else:
            message = f"❌ {players[current_player]['name']} промахнулся!"
            
            # Показываем эффект прицеливания даже при промахе
            if players[current_player]['aim'] > 0:
                message += f"\n💫 Несмотря на прицеливание (+{players[current_player]['aim'] * 25}%)..."
        
        # Сбрасываем прицел после броска
        players[current_player]['aim'] = 0
        # Бросок передает ход
        game['current_turn'] = opponent_id
    
    # Проверка конца игры
    if players[current_player]['hp'] <= 0 or players[opponent_id]['hp'] <= 0:
        if players[current_player]['hp'] <= 0:
            winner = players[opponent_id]['name']
            loser = players[current_player]['name']
        else:
            winner = players[current_player]['name']
            loser = players[opponent_id]['name']
        
        result_text = (
            f"⚔️ *ДУЭЛЬ ЗАВЕРШЕНА!*\n\n"
            f"🏆 *ПОБЕДИТЕЛЬ:* {winner}\n"
            f"💀 *ПРОИГРАВШИЙ:* {loser}\n\n"
            f"⚡ by {CREATOR}"
        )
        
        # Отправляем результат обоим игрокам
        for pid in [current_player, opponent_id]:
            try:
                await context.bot.send_message(chat_id=pid, text=result_text, parse_mode='Markdown')
            except:
                pass
        
        # Уведомляем в исходном чате о результате
        original_chat_id = game.get('original_chat_id')
        if original_chat_id:
            try:
                await context.bot.send_message(
                    chat_id=original_chat_id,
                    text=f"⚔️ *РЕЗУЛЬТАТ ДУЭЛИ:*\n🏆 ПОБЕДИТЕЛЬ: {winner}\n💀 ПРОИГРАВШИЙ: {loser}",
                    parse_mode='Markdown'
                )
            except:
                pass
        
        # Удаляем игру из хранилища
        if game_id in games:
            del games[game_id]
        if current_player in player_games:
            del player_games[current_player]
        if opponent_id in player_games:
            del player_games[opponent_id]
            
        return
    
    # Обновляем сообщения для обоих игроков
    current_turn_name = players[game['current_turn']]['name']
    
    # Показываем текущие прицелы игроков
    aim_info = ""
    for pid, pdata in players.items():
        if pdata['aim'] > 0:
            aim_info += f"🎯 {pdata['name']}: +{pdata['aim'] * 25}%\n"
    
    game_text = (
        f"⚔️ *ДУЭЛЬ*\n\n"
        f"🔪 {players[current_player]['name']}: ❤️ {players[current_player]['hp']} HP\n"
        f"🔪 {players[opponent_id]['name']}: ❤️ {players[opponent_id]['hp']} HP\n\n"
    )
    
    if aim_info:
        game_text += f"*Прицелы:*\n{aim_info}\n"
    
    game_text += f"*Сейчас ход:* {current_turn_name}\n\n{message}"
    
    # Обновляем сообщение для текущего игрока
    await query.edit_message_text(
        text=game_text,
        reply_markup=game_keyboard_pvp(game_id, user_id, user_id == game['current_turn']),
        parse_mode='Markdown'
    )
    
    # Обновляем сообщение для оппонента
    try:
        await context.bot.send_message(
            chat_id=opponent_id,
            text=game_text,
            reply_markup=game_keyboard_pvp(game_id, opponent_id, opponent_id == game['current_turn']),
            parse_mode='Markdown'
        )
    except Exception as e:
        logging.error(f"Ошибка отправки сообщения оппоненту: {e}")
    
    await query.answer()

def game_keyboard_pve():
    """Клавиатура для PvE"""
    keyboard = [
        [
            InlineKeyboardButton("🎯 Прицелиться", callback_data="aim"),
            InlineKeyboardButton("🔪 Кинуть нож", callback_data="throw")
        ],
        [InlineKeyboardButton("🔄 Новая игра", callback_data="battle_bot")],
        [InlineKeyboardButton("⬅️ Главное меню", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)

def game_keyboard_pvp(game_id: str, player_id: int, is_current_turn: bool = True):
    """Клавиатура для PvP с новой кнопкой"""
    # Извлекаем ID игроков из game_id
    parts = game_id.split('_')
    if len(parts) >= 3:
        p1_id = parts[1]
        p2_id = parts[2]
        short_game_id = f"{p1_id}_{p2_id}"
    else:
        short_game_id = game_id
    
    if is_current_turn:
        keyboard = [
            [
                InlineKeyboardButton("🎯 Прицелиться", callback_data=f"pvp_aim_{short_game_id}"),
                InlineKeyboardButton("🔪 Кинуть нож", callback_data=f"pvp_throw_{short_game_id}")
            ],
            [
                InlineKeyboardButton("🌀 Сбить прицел", callback_data=f"pvp_disrupt_{short_game_id}")
            ]
        ]
    else:
        keyboard = [
            [InlineKeyboardButton("⏳ Ожидайте ход противника...", callback_data="wait")]
        ]
    
    return InlineKeyboardMarkup(keyboard)

async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Возврат в главное меню"""
    query = update.callback_query
    await query.answer()
    await start(update, context)

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Статистика"""
    query = update.callback_query
    await query.answer()
    
    text = "📊 *Статистика*\n\n(функция в разработке)\n\nСкоро здесь будет ваша статистика побед и поражений!"
    
    keyboard = [[InlineKeyboardButton("⬅️ Назад в меню", callback_data="main_menu")]]
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

async def set_commands(application: Application):
    """Установка команд меню"""
    commands = [
        BotCommand("start", "Запустить бота"),
        BotCommand("help", "Помощь"),
        BotCommand("duel", "Вызвать на дуэль")
    ]
    await application.bot.set_my_commands(commands)

def main():
    """Основная функция"""
    try:
        application = Application.builder().token(BOT_TOKEN).build()
        
        # Обработчики команд
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", start))
        application.add_handler(CommandHandler("duel", start))
        
        # Обработчики callback
        application.add_handler(CallbackQueryHandler(about_creators, pattern="^about_creators$"))
        application.add_handler(CallbackQueryHandler(challenge_info, pattern="^challenge_info$"))
        application.add_handler(CallbackQueryHandler(battle_bot, pattern="^battle_bot$"))
        application.add_handler(CallbackQueryHandler(stats, pattern="^stats$"))
        application.add_handler(CallbackQueryHandler(main_menu, pattern="^main_menu$"))
        application.add_handler(CallbackQueryHandler(handle_challenge_response, pattern="^(accept|decline)_"))
        application.add_handler(CallbackQueryHandler(handle_game_action, pattern="^(aim|throw|disrupt|pvp_)"))
        
        # Обработчик сообщений
        application.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND, 
            handle_all_messages
        ))
        
        print("🚀 Бот запущен на Railway!")
        print("📝 Для вызова: ответьте на сообщение игрока словом 'Сразить' или 'Дуэль'")
        
        # Запускаем бота
        application.run_polling()
        
    except Exception as e:
        logging.error(f"❌ Ошибка запуска бота: {e}")

if __name__ == "__main__":
    main()
