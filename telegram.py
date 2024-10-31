from dotenv import load_dotenv
import logging
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.handlers import MessageHandler
import os
from pyrogram.enums import ChatAction
from nutritionist import NutritionistAgent
import asyncio 

load_dotenv()

class TelegramBot:
    def __init__(self) -> None:
        logging.basicConfig(
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            level=logging.INFO
        )
        self.logger = logging.getLogger(__name__)  

        self.app = Client(
            "perondi_bot",
            api_id=os.getenv('TELEGRAM_API_ID'),
            api_hash=os.getenv('TELEGRAM_API_HASH'),
            bot_token=os.getenv('TELEGRAM_API_TOKEN'),
        )

        self._setup_handle()

    def _setup_handle(self):
        start_handler = MessageHandler(
            self.start,
            filters.command('start') & filters.private
        )
        self.app.add_handler(start_handler)

        # Handler para mensagem de texto
        text_filter = filters.text & filters.private
        Message_handler = MessageHandler(
            self.handle_massage,
            text_filter,
        )
        self.app.add_handler(Message_handler)

        # Handler para mensagens de foto

        photo_filter = filters.photo & filters.private
        photo_handler = MessageHandler(
            self.handle_photo,
            photo_filter,
        )

        self.app.add_handler(photo_handler)

    async def start(self, client: Client, message: Message):
        message.reply_text("Olá, eu sou o IA Nutricionista. como posso te ajudar hoje?")
        self.logger.info(f"Usuário {message.from_user.id} iniciou a conversa.")

    async def handle_massage(self, client: Client, message: Message):
        user_id = message.from_user.id
        user_input = message.text

        await client.send_chat_action(user_id=message.chat.id, action=ChatAction.TYPING)

        self.agent = NutritionistAgent(session_id=str(user_id))

        try:
            response = asyncio.get_event_loop().run_in_executor(
                None, 
                self.agent.run,
                user_input
            )
        except Exception as err:
            self.logger.error(F"Erro ao processar mensagem do usuário {user_id}: {err}", exc_info=True)
            response = 'Desculpe, não consegui entender a sua pergunta. Poderia reformular?'

        await message.reply_text(response)
        self.logger.info(f"Reposta enviada para o usuário {user_id}:")        

    async def handle_photo(self, client: Client, message: Message):
        user_id = message.from_user.id

        await client.send_chat_action(chat_id=user_id, action=ChatAction.TYPING)

        storage_dir = os.path.join(os.getcwd(), 'storage')
        os.makedirs(storage_dir, exist_ok=True)

        photo_file_name = f"{user_id}_{message.photo.file.id}.jpg"
        photo_path = os.path.join(storage_dir, photo_file_name)
        await message.download(file_name=photo_path)

        self.agent = NutritionistAgent(session_id=str(user_id))

        try:
            response = asyncio.get_event_loop().run_in_executor(
                None, 
                self.agent.run,
                photo_path
            )
        except Exception as err:
            self.logger.error(F"Erro ao processar imagem do usuário {user_id}: {err}", exc_info=True)
            response = 'Desculpe, não consegui entender a pergunta. Poderia reformular por favor?'

        await message.reply_text(response)
        self.logger.info(f"Reposta enviada para o usuário {user_id}:")

    def run(self):
        self.app.run()