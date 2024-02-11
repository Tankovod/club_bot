from typing import Literal

from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


class EventsCallbackData(CallbackData, prefix='us'):
    event: Literal["man", "talk"]


events = {
    "man": {"name": "Мужской клуб", "description": "Информация о клубе",
            "photo": "https://sp.onliner.by/wp-content/uploads/2020/08/Untitled-19.png", "callback": "man"},
    "talk": {"name": "Разговорный клуб", "description": "Информация о клубе",
             "photo": "https://cdn-user30887.skyeng.ru/uploads/63a2ca2b70a3b279014270.jpg", "callback": "talk"}
}

events_ik = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text=event.get("name"),
                              callback_data=EventsCallbackData(event=event.get("callback")).pack())]
        for event in events.values()
    ]
)


class InlineClubInfo:
    def __init__(self, event):
        self.event = event

    def create_keyboard(self):
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=f"Остановить уведомления ({events.get(self.event).get('name')})",
                                  callback_data=f"stop_{self.event}")]
        ])


