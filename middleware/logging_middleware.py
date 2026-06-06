import logging
from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

async def logging_middleware(update: Update, context: ContextTypes.DEFAULT_TYPE, next_handler):
    if update.message:
        logger.info(f"Message from {update.effective_user.id}: {update.message.text}")
    return await next_handler()
