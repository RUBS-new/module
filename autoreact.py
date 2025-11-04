# ========================
# ✨ DEVELOPER: @RUBS_New ✨
# ========================

# meta developer: @RUBS_New
# meta name: AutoReact
# scope: hikka_only
# meta version: 1.1.0 

import random
from telethon import events
from .. import loader, utils
from herokutl.tl.types import Message


@loader.tds
class AutoReactMod(loader.Module):
    """Автоматические реакции на сообщения"""

    strings = {
        "name": "AutoReact",
        "no_trigger": "❌ Укажите слово-триггер",
        "no_reaction": "❌ Укажите эмодзи-реакцию",
        "reaction_added": "✅ Добавлена реакция {} на триггер '{}'",
        "reaction_exists": "⚠️ Реакция на '{}' уже существует",
        "reaction_removed": "✅ Удалена реакция на триггер '{}'",
        "no_reactions": "ℹ️ Нет настроенных реакций",
        "reaction_list": "📝 Список автореакций:\n\n{}",
        "chat_enabled": "✅ Автореакции включены в этом чате",
        "chat_disabled": "🚫 Автореакции выключены в этом чате",
        "all_cleared": "🗑 Все автореакции очищены",
    }

    def __init__(self):
        self.config = loader.ModuleConfig(
            "disabled_chats",
            [],
            "ID чатов, где автореакции отключены"
        )
        self.reactions = {}

    async def client_ready(self, client, db):
        """Инициализация при загрузке."""
        self._client = client
        self._db = db
        
        self.reactions = self._db.get(self.strings["name"], "reactions", {})
        
        try:
            client.add_event_handler(
                self._message_handler,
                events.NewMessage()
            )
        except Exception:
            pass

    async def _message_handler(self, event):
        """Проверяет сообщения на триггеры и добавляет реакции."""
        try:
            if event.chat_id in self.config["disabled_chats"]:
                return

            if event.out:
                return

            if not event.message.text:
                return

            text = event.message.text.lower()
            for trigger, reactions in self.reactions.items():
                if trigger.lower() in text:
                    reaction = random.choice(reactions.split('|'))
                    await event.message.react(reaction)
                    
        except Exception:
            return

    def _save_reactions(self):
        """Сохраняет реакции в БД."""
        self._db.set(self.strings["name"], "reactions", self.reactions)

    async def araddcmd(self, message: Message):
        """Добавить автореакцию: .араdd триггер эмодзи"""
        args = utils.get_args_raw(message).split(maxsplit=1)
        
        if len(args) < 1:
            await utils.answer(message, self.strings["no_trigger"])
            return
        
        if len(args) < 2:
            await utils.answer(message, self.strings["no_reaction"])
            return

        trigger, reaction = args
        
        if trigger in self.reactions:
            await utils.answer(
                message,
                self.strings["reaction_exists"].format(trigger)
            )
            return

        self.reactions[trigger] = reaction
        self._save_reactions()
        
        await utils.answer(
            message,
            self.strings["reaction_added"].format(reaction, trigger)
        )

    async def ardelcmd(self, message: Message):
        """Удалить автореакцию: .аrdel триггер"""
        args = utils.get_args_raw(message)
        
        if not args:
            await utils.answer(message, self.strings["no_trigger"])
            return

        if args not in self.reactions:
            await utils.answer(
                message,
                self.strings["reaction_exists"].format(args)
            )
            return

        del self.reactions[args]
        self._save_reactions()
        
        await utils.answer(
            message,
            self.strings["reaction_removed"].format(args)
        )

    async def arlistcmd(self, message: Message):
        """Показать список автореакций: .arlist"""
        if not self.reactions:
            await utils.answer(message, self.strings["no_reactions"])
            return

        text = []
        for trigger, reaction in self.reactions.items():
            text.append(f"• {trigger}: {reaction}")

        await utils.answer(
            message,
            self.strings["reaction_list"].format("\n".join(text))
        )

    async def artogglecmd(self, message: Message):
        """Включить/выключить реакции в чате: .artoggle"""
        chat_id = utils.get_chat_id(message)
        
        if chat_id in self.config["disabled_chats"]:
            self.config["disabled_chats"].remove(chat_id)
            await utils.answer(message, self.strings["chat_enabled"])
        else:
            self.config["disabled_chats"].append(chat_id)
            await utils.answer(message, self.strings["chat_disabled"])

    async def arclearcmd(self, message: Message):
        """Очистить все автореакции: .arclear"""
        self.reactions.clear()
        self._save_reactions()
        await utils.answer(message, self.strings["all_cleared"])

    async def on_unload(self):
        """Выгрузка модуля."""
        try:
            if self._client:
                self._client.remove_event_handler(self._message_handler)
        except Exception:
            pass