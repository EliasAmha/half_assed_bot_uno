import logging
import os
import uuid

import dotenv
from aiogram import Bot, Dispatcher, executor, types

from literals import *
from utils import *

dotenv.load_dotenv()
logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(BOT_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
  await message.reply(WELCOME_MESSAGE)

@dp.inline_handler()
async def query_handler(inline_query):
  query = inline_query.query
  count, phrases = get_results(query)
  results = []
  for phrase in phrases:
    title = f"{phrase.title}: {phrase.quote}"
    results.append(types.InlineQueryResultArticle( 
      id=str(uuid.uuid4()),
      title=title,
      input_message_content=types.InputTextMessageContent(
        f"{phrase.url} \n\n {phrase.title}: {phrase.quote}"
      ),
    ))
  if results:
    await bot.answer_inline_query(inline_query.id, results=results, cache_time=1)
  else:
    await bot.answer_inline_query(inline_query.id, results=[
      types.InlineQueryResultArticle(
        id=str(uuid.uuid4()),
        title="No results, sowwy 😢",
        input_message_content=types.InputTextMessageContent(
          "No results, sowwy 😢"
        )
      )
    ], cache_time=1)
  
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
