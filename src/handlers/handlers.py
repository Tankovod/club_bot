from datetime import datetime

from aiogram import Router, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery
from sqlalchemy import select, delete
from sqlalchemy.exc import IntegrityError

from src.database.models import User, Role, UserClub, Club
from src.keyboards.inline.ik import EventsCallbackData, ActionCallbackData, create_club_ik, back_button_clubs, \
    create_user_clubs_ikb, ClubIdCallbackData, ClubNewsletterCallbackData, create_club_newsletter_ik
from src.settings import bot

router = Router()


class ConfigClubs(StatesGroup):
    select_clubs = State()


class Newsletter(StatesGroup):
    select_clubs = State()
    send_message = State()


@router.message(Command("start"))
async def first_event_info(message: Message):
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
        except IntegrityError as ex:
            print(ex)
            await message.answer(text=f"Рады видеть Вас снова, {message.chat.first_name}")
            return None

        await session.refresh(new_user)

        clubs_ids = await session.scalars(select(Club.id))
        user_clubs = [UserClub(club_id=club_id, user_id=message.chat.id) for club_id in clubs_ids]

        session.add_all(user_clubs)
        await session.commit()
        for user_club in user_clubs:
            await session.refresh(user_club)

        await message.answer(text=f"Приветствуем Вас,"
                                  f" {message.chat.first_name if message.chat.first_name else message.chat.username}!"
                                  f" ☺️ \nДля настройки уведомлений о предстоящих мероприятиях нажмите /edit")


@router.message(Command("events"))
async def first_events(message: Message):
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    await message.answer(reply_markup=await create_club_ik(), text="Список Клубов:")


@router.callback_query(EventsCallbackData.filter())
async def get_event_info(callback: CallbackQuery, callback_data: EventsCallbackData):
    await bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)
    if callback_data.back_to_menu is True:
        await callback.message.answer(reply_markup=await create_club_ik(), text="Список Клубов:")
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


@router.message(Command("edit"))
async def user_club_config(message: Message, state: FSMContext):
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    async with UserClub.session() as session:
        all_clubs = await session.scalars(select(Club))
        all_clubs = {club.id: club.name for club in all_clubs}

        user_clubs_ids = await session.scalars(select(UserClub.club_id)
                                               .filter(UserClub.user_id == message.chat.id))
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


@router.callback_query(ActionCallbackData.filter(F.action == "save"), ConfigClubs.select_clubs)
async def cancel_or_save_config(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if not data.get("user_clubs_ids"):
        await callback.answer(text="🛑 Выберите хотя бы один клуб ", show_alert=True)
        return None

    async with UserClub.session() as session:
        await session.execute(delete(UserClub)
                              .where(UserClub.user_id == callback.message.chat.id))

        await session.commit()

        session.add_all(
            [UserClub(user_id=callback.message.chat.id, club_id=club_id) for club_id in data.get("user_clubs_ids")]
        )
        await session.commit()

        await callback.message.edit_text(text="Фильтр сохранен! Ждите новых сообщений 😼")
        await state.clear()


@router.callback_query(ActionCallbackData.filter(F.action == "cancel"), ConfigClubs.select_clubs)
async def cancel_or_save_config(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(text="Отмена")
    await state.clear()


@router.message(Command("send"))
async def start_send_newsletter(message: Message, state: FSMContext):
    async with User.session() as session:
        user: User = await session.scalar(select(User).filter(User.tg_id == message.chat.id))

        if user.user_role.name == "admin":
            await message.answer(text="Выберите клуб для рассылки:", reply_markup=await create_club_newsletter_ik())
            await state.set_state(Newsletter.select_clubs)
        else:
            await message.answer(text="У Вас недостаточно прав.")


@router.callback_query(ClubNewsletterCallbackData.filter(), Newsletter.select_clubs)
async def select_club_before_newsletter(callback: CallbackQuery, callback_data: EventsCallbackData, state: FSMContext):
    await state.set_data(data={"club_id": callback_data.club_id})
    await callback.message.edit_text(text="Отправьте текст оповещения:")
    await state.set_state(Newsletter.send_message)


@router.message(Newsletter.send_message)
async def make_newsletter(message: Message, state: FSMContext):
    data = await state.get_data()
    async with UserClub.session() as session:
        users_ids = await session.scalars(select(UserClub.user_id).filter(UserClub.club_id == data.get("club_id")))

        await state.clear()
        for user_id in users_ids:
            try:
                await bot.send_message(chat_id=user_id, text=message.text)
            except TelegramBadRequest:
                print(f"TelegramBadRequest, user_id: {user_id}")
        else:
            await message.answer(text="Рассылка завершена!")


@router.message(Command("about"))
async def handle_about(message: Message):
    await message.answer(
        text="  Данный бот помогает найти подходящие мероприятия и классно провести время.\n    По организационным "
             "вопросам обращаться @ZDES_BY"
    )
