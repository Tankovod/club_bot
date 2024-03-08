from typing import Literal, Optional

from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy import select

from src.database.models import Club


class EventsCallbackData(CallbackData, prefix='us'):
    event: Optional[str] = None
    back_to_menu: Optional[bool] = False


class ActionCallbackData(CallbackData, prefix="ac"):
    action: Literal["back", "cancel", "save"]


class ClubIdCallbackData(CallbackData, prefix="fi"):
    club_id: int


class ClubNewsletterCallbackData(CallbackData, prefix="nl"):
    club_id: int


async def create_club_ik() -> InlineKeyboardMarkup:
    async with Club.session() as session:
        clubs = await session.scalars(select(Club))

        return InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text=club.name,
                                      callback_data=EventsCallbackData(event=club.tag).pack())]
                for club in clubs.unique()
            ]
        )


async def create_club_newsletter_ik() -> InlineKeyboardMarkup:
    async with Club.session() as session:
        clubs = await session.scalars(select(Club))

        return InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text=club.name,
                                      callback_data=ClubNewsletterCallbackData(club_id=club.id).pack())]
                for club in clubs.unique()
            ]
        )


back_button_clubs = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text=" ⬅️  НАЗАД ", callback_data=EventsCallbackData(back_to_menu=True).pack())]
    ]
)


async def create_user_clubs_ikb(all_clubs: dict[int: str], user_clubs_ids: list[int]) -> InlineKeyboardMarkup:
    ikb = []
    for club in all_clubs.items():
        if club[0] in user_clubs_ids:
            ikb.append(
                [InlineKeyboardButton(
                    callback_data=ClubIdCallbackData(club_id=club[0]).pack(),
                    text="✅ " + club[1]
                )]
            )
            continue
        ikb.append(
            [InlineKeyboardButton(
                callback_data=ClubIdCallbackData(club_id=club[0]).pack(),
                text=club[1]
            )]
        )

    return InlineKeyboardMarkup(
        inline_keyboard=[*ikb,
                         [InlineKeyboardButton(text="ОТМЕНА", callback_data=ActionCallbackData(action="cancel").pack()),
                          InlineKeyboardButton(text="СОХРАНИТЬ",
                                               callback_data=ActionCallbackData(action="save").pack())],
                         ]
    )
