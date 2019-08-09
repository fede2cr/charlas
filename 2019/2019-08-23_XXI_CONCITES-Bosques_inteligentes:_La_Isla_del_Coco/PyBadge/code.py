"""
This is a Conference Badge type Name Tag that is intended to be displayed on
the PyBadge. Feel free to customize it to your heart's content.
"""

from adafruit_pybadger import PyBadger

pybadger = PyBadger()

pybadger.show_badge(name_string="Alvaro", hello_string="CONCITES", my_name_is_string="XII", hello_scale=2, my_name_is_scale=2, name_scale=3, background_color=0x00FF00)

while True:
    # Reading buttons too fast returns 0
    if pybadger.button.a:
        pybadger.show_business_card(image_name="greencore.bmp", name_string="Alvaro", name_scale=2,
            email_string_one="", email_string_two="@greencore.co.cr")
    elif pybadger.button.b:
        pybadger.show_qr_code(data="https://www.greencore.co.cr")
    elif pybadger.button.start:
        pybadger.show_badge(name_string="Alvaro", hello_string="CONCITES", my_name_is_string="XII", hello_scale=2, my_name_is_scale=2, name_scale=3, background_color=0x00FF00)