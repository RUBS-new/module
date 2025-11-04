# ========================
# ✨ DEVELOPER: @RUBS_New ✨
# ========================

# meta developer: @RUBS_New
# meta banner: https://raw.githubusercontent.com/RUBS-new/Heroku-Modules/refs/heads/main/banner/banner_newyear.png
# meta pic: https://raw.githubusercontent.com/RUBS-new/Heroku-Modules/refs/heads/main/banner/banner_newyear.png
# meta name: NewYearCountdown
# scope: hikka_only
# meta version: 1.1.3 

import datetime
import random
from .. import loader, utils
from telethon.tl.patched import Message

DEFAULT_BANNER_URL = "https://raw.githubusercontent.com/RUBS-new/Heroku-Modules/refs/heads/main/banner/banner_newyear.png"

@loader.tds
class NewYearCountdownMod(loader.Module):
    """Показывает, сколько осталось до Нового года."""

    def config_complete(self):
        if self.config["Banner URL"] == "CHANGE_ME":
            self.config["Banner URL"] = DEFAULT_BANNER_URL

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "Banner URL",
                "CHANGE_ME",
                lambda: "URL-адрес картинки для отображения вместе с отсчётом. "
                        "Если URL не задан, используется баннер из метаданных модуля.",
            )
        )
        self.messages = [
            "✨ Скоро будет ёлка и мандарины! ✨",
            "🎁 Пора готовить подарки! 🎁",
            "🌟 Новый год уже совсем близко! 🌟",
            "💫 Время загадывать желания! 💫",
            "🍽️ Готовьте оливье! 🍽️",
            "🎄 Скоро будем наряжать ёлку! 🎄",
            "🎅 Дед Мороз уже в пути! 🎅",
            "📝 Пора писать список желаний! ✨",
            "✨ Скоро будет самая волшебная ночь в году! ✨",
            "🌠 Время чудес приближается! 🌠",
            "❄️ Пусть Новый год принесёт много радости! ❄️",
            "🎆 До волшебства осталось совсем немного! 🎆"
        ]

    strings = {
        "name": "NewYearCountdown",
        "countdown": (
            "🎄 <b>══════ New Year {next_year} ══════</b> 🎄\n\n"
            "<emoji document_id=5298599677461216652>🎆</emoji> <b>До Нового {next_year} года осталось:</b>\n\n"
            "<blockquote>🎇 <b>Дней:</b> <code>{days}</code>\n"
            "❄️ <b>Часов:</b> <code>{hours}</code>\n"
            "🎁 <b>Минут:</b> <code>{minutes}</code>\n"
            "⭐️ <b>Секунд:</b> <code>{seconds}</code></blockquote>\n\n"
            "🎅 <i>{message}</i>\n\n"
            "❆═══════════════════════❆"
        ),
        "no_photo": "<b>🎄 До Нового {next_year} года осталось:</b>\n\n{countdown_text}\n\n<i>⚠️ Баннер не найден. Проверьте настройки модуля.</i>"
    }
    
    def _get_countdown(self):
        now = datetime.datetime.now()
        next_year = now.year + 1
        new_year = datetime.datetime(next_year, 1, 1)
        delta = new_year - now

        days = delta.days
        hours = delta.seconds // 3600
        minutes = (delta.seconds % 3600) // 60
        seconds = delta.seconds % 60

        message = random.choice(self.messages)

        return {
            "next_year": next_year,
            "days": days,
            "hours": hours,
            "minutes": minutes,
            "seconds": seconds,
            "message": message
        }

    @loader.command(ru_doc="Показать отсчёт до Нового года")
    async def newyear(self, message: Message):
        
        countdown = self._get_countdown()
        caption_text = self.strings["countdown"].format(**countdown)
        
        photo_url = self.config["Banner URL"]

        if photo_url and photo_url != "CHANGE_ME":
            try:
                await message.client.send_file(
                    message.to_id, 
                    photo_url, 
                    caption=caption_text, 
                    parse_mode="HTML" 
                )
                await message.delete() 
            except Exception as e:
                text_only = caption_text.replace("🎄 <b>══════ New Year {next_year} ══════</b> 🎄\n\n".format(**countdown), "")
                output = self.strings["no_photo"].format(next_year=countdown["next_year"], countdown_text=text_only)
                output += f"\n\n<i>(Ошибка: {e})</i>"
                await utils.answer(message, output)
        else:
            text_only = caption_text.replace("🎄 <b>══════ New Year {next_year} ══════</b> 🎄\n\n".format(**countdown), "")
            output = self.strings["no_photo"].format(next_year=countdown["next_year"], countdown_text=text_only)
            await utils.answer(message, output)