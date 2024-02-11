from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from src.settings import bot
from src.keyboards.inline.ik import events_ik, EventsCallbackData, events, InlineClubInfo

router = Router()


@router.message(Command("start"))
async def first_event_info(message: Message):
    await message.answer(text="Приветствуем Вас!")


@router.message(Command("events"))
async def first_events(message: Message):
    await message.answer(reply_markup=events_ik, text="Список мероприятий:")


@router.callback_query(EventsCallbackData.filter())
async def get_event_info(callback: CallbackQuery, callback_data: EventsCallbackData):
    await bot.send_photo(
        chat_id=callback.message.chat.id,
        photo=events.get(callback_data.event).get("photo"),
        caption=events.get(callback_data.event).get("description"),
        reply_markup=InlineClubInfo(event=callback_data.event).create_keyboard()
    )

