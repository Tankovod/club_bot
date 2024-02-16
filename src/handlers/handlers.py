from aiogram import Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from datetime import datetime
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy import select, delete
from sqlalchemy.exc import IntegrityError
from aiogram.methods import get_user_profile_photos
from src.database.models import User, Role, UserClub, Club

from src.settings import bot
from src.keyboards.inline.ik import EventsCallbackData, ActionCallbackData, \
    create_club_ik, back_button_clubs, create_user_clubs_ikb, ClubIdCallbackData

router = Router()

class ConfigClubs(StatesGroup):
    select_clubs = State()
    save_clubs = State()


@router.message(Command("start"))
async def first_event_info(message: Message):
    await message.answer(str(message.photo[0]))
    async with User.session() as session:
        new_user = User(
            tg_id=message.chat.id,
            username=message.chat.username,
            first_name=message.chat.first_name,
            last_name=message.chat.last_name,
            date_sign_up=datetime.now(),
            role_id=select(Role.id).filter(Role.name == "user")
        )
        session.add(new_user)

        try:
            await session.commit()
        except IntegrityError:
            await message.answer(text=f"Рады видеть Вас снова, {message.chat.first_name}")
            return None

        await session.refresh(new_user)

        clubs_ids = await session.scalars(select(Club.id))
        user_clubs = [UserClub(club_id=club_id, user_id=new_user.id) for club_id in clubs_ids]

        session.add_all(user_clubs)
        await session.commit()
        for user_club in user_clubs:
            await session.refresh(user_club)

        await message.answer(text=f"Приветствуем Вас,"
                                  f" {message.chat.first_name if message.chat.first_name else message.chat.username}! ☺️"
                                  f"Для настройки уведомлений о предстоящих мероприятиях нажмите /edit")


@router.message(Command("events"))
async def first_events(message: Message):
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    await message.answer(reply_markup=await create_club_ik(), text="Список Клубов:")


@router.callback_query(EventsCallbackData.filter())
async def get_event_info(callback: CallbackQuery, callback_data: EventsCallbackData):
    await bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)

    if callback_data.event == "back":
        await callback.message.answer(reply_markup=await create_club_ik(), text="Список клубов")
        return None

    async with Club.session() as session:
        club_info = await session.scalar(select(Club).filter(Club.tag == callback_data.event))

        if club_info.photo:

            await bot.send_photo(
                chat_id=callback.message.chat.id,
                photo=club_info.photo,
                caption=club_info.description,
                reply_markup=back_button_clubs
            )

        else:
            await callback.message.answer(text=club_info.description, reply_markup=back_button_clubs)
            # await callback.message.edit_text(text=club_info.description)
            # await callback.message.edit_reply_markup(
            #     reply_markup=back_button_clubs
            # )


@router.message(Command("edit"))
async def user_club_config(message: Message, state: FSMContext):
    async with UserClub.session() as session:
        all_clubs = await session.scalars(select(Club))
        all_clubs = {club.id: club.name for club in all_clubs}

        user_clubs_ids = await session.scalars(select(UserClub.club_id)
                                               .filter(UserClub.user_id == select(User.id)
                                                       .filter(User.tg_id == message.chat.id)))
        user_clubs_ids = user_clubs_ids.all()

        await message.answer(reply_markup=await create_user_clubs_ikb(all_clubs=all_clubs, user_clubs_ids=user_clubs_ids),
                             text="Выберите интересующие клубы:")
        await state.set_state(ConfigClubs.select_clubs)
        await state.set_data({"user_clubs_ids": user_clubs_ids, "all_clubs": all_clubs})


@router.callback_query(ClubIdCallbackData.filter(), ConfigClubs.select_clubs)
async def handle_action(callback: CallbackQuery, callback_data: ClubIdCallbackData, state: FSMContext):
    data = await state.get_data()
    if callback_data.club_id in data.get("user_clubs_ids"):
        data["user_clubs_ids"].remove(callback_data.club_id)
    else:
        data["user_clubs_ids"].append(callback_data.club_id)

    await state.set_data(data=data)
    await callback.message.edit_reply_markup(reply_markup=await create_user_clubs_ikb(
        all_clubs=data.get("all_clubs"),
        user_clubs_ids=data.get("user_clubs_ids")
    ))


@router.callback_query(ActionCallbackData.filter(), ConfigClubs.select_clubs)
async def cancel_or_save_config(callback: CallbackQuery, callback_data: ActionCallbackData, state: FSMContext):
    if callback_data.action == "save":
        data = await state.get_data()

        async with UserClub.session() as session:
            user_id: int = await session.scalar(select(User.id).filter(User.tg_id == callback.message.chat.id))
            await session.execute(delete(UserClub)
                                  .where(UserClub.user_id == user_id))

            await session.commit()

            session.add_all(
                [UserClub(user_id=user_id, club_id=club_id) for club_id in data.get("user_clubs_ids")]
            )
            await session.commit()

            await callback.message.edit_text(text="Фильтр успешно сохранен!")
            await state.clear()

