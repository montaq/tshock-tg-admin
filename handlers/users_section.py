import logging

from aiogram import Router
from aiogram.filters import StateFilter, Text, or_f
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from filters.auth import IsAuth
from keyboards.keyboard_utils import create_inline_kb
from keyboards.keyboards import main_menu_kb, users_section_menu_kb
from lexicon.default.message_texts import MAIN_MENU_TEXT
from lexicon.users_section.message_texts import USERS_SECTION_MENU_TEXT
from states.states import FSMUsersSection

router: Router = Router()
router.message.filter(IsAuth(), StateFilter(FSMUsersSection))
router.callback_query.filter(IsAuth(), StateFilter(FSMUsersSection))

log: logging.Logger = logging.getLogger('users_section')


@router.callback_query(StateFilter(FSMUsersSection.menu), Text(text='back'))
async def process_back_to_main_menu(callback: CallbackQuery, state: FSMContext, language: str):
    await callback.message.delete()
    await callback.message.answer(text=MAIN_MENU_TEXT[language], reply_markup=main_menu_kb(language))
    await state.clear()


@router.callback_query(StateFilter(FSMUsersSection.menu), Text(text='active_users'))
async def process_active_users(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await callback.message.answer(text='List of active users...',
                                  reply_markup=create_inline_kb(1, {'back': '<< Back'}))

    await state.set_state(FSMUsersSection.active_users)


@router.callback_query(StateFilter(FSMUsersSection.menu), Text(text='all_users'))
async def process_all_users(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await callback.message.answer(text='List of all registered users...',
                                  reply_markup=create_inline_kb(1, {'back': '<< Back'}))

    await state.set_state(FSMUsersSection.all_users)


@router.callback_query(or_f(StateFilter(FSMUsersSection.active_users),
                            StateFilter(FSMUsersSection.all_users)),
                       Text(text='back'))
async def process_back_to_users_section_menu(callback: CallbackQuery, state: FSMContext, language: str):
    await callback.message.delete()
    await callback.message.answer(text=USERS_SECTION_MENU_TEXT[language],
                                  reply_markup=users_section_menu_kb(language))
    await state.set_state(FSMUsersSection.menu)