from pyrogram import Client

# api_id — число, api_hash — строка в кавычках
app = Client(
    name="controller_bot", 
    api_id=35855801, 
    api_hash="3752f44e12436e8d2cffcf439a576d52",
    workdir="."
)

print("Сейчас нужно будет ввести номер телефона и код из Telegram...")
app.run()