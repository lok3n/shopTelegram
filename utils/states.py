from aiogram.fsm.state import State, StatesGroup


class Admin(StatesGroup):
    edit_info_text = State()
    edit_pay_text = State()

    add_location = State()

    input_text_mailing = State()

    input_product_photo = State()
    input_product_description = State()
    input_product_price = State()
    submit = State()


class AddYoomoney(StatesGroup):
    input_name = State()
    input_clientId = State()
    input_clientSecret = State()
    input_redirectUrl = State()
    input_code = State()
