import logging
from typing import AsyncGenerator

from fastapi import Request

logger = logging.getLogger(__name__)


class TelegramStreamer:
    """
    Telegram media streaming helper.
    Compatible with Pyrogram Client.stream_media().
    """

    def __init__(self, app_bot):
        self.app_bot = app_bot

    async def stream(
        self,
        message,
        request: Request,
    ) -> AsyncGenerator[bytes, None]:
        """
        Stream Telegram media.

        Stops immediately if client disconnects.
        """

        try:

            async for chunk in self.app_bot.stream_media(message):

                if await request.is_disconnected():

                    logger.info(
                        "Client disconnected while streaming."
                    )

                    break

                yield chunk

        except Exception:

            logger.exception(
                "Telegram streaming failed."
            )

            raise