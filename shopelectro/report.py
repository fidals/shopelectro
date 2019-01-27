import typing

from django.conf import settings
from telegram import Bot


class TelegramReport:

    def __init__(self):
        self.bot = Bot(settings.TG_BOT_TOKEN)

    def send(self, text: str):
        for id in settings.TG_REPORT_ADDRESSEES:
            self.bot.send_message(id, text)
