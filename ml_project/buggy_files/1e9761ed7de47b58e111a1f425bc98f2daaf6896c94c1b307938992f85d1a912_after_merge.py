def send_msg(msg: str, bot: Bot = None, parse_mode: ParseMode = ParseMode.MARKDOWN) -> None:
    """
    Send given markdown message
    :param msg: message
    :param bot: alternative bot
    :param parse_mode: telegram parse mode
    :return: None
    """
    if not is_enabled():
        return

    bot = bot or _UPDATER.bot

    try:
        try:
            bot.send_message(_CONF['telegram']['chat_id'], msg, parse_mode=parse_mode)
        except NetworkError as network_err:
            # Sometimes the telegram server resets the current connection,
            # if this is the case we send the message again.
            logger.warning(
                'Got Telegram NetworkError: %s! Trying one more time.',
                network_err.message
            )
            bot.send_message(_CONF['telegram']['chat_id'], msg, parse_mode=parse_mode)
    except TelegramError as telegram_err:
        logger.warning('Got TelegramError: %s! Giving up on that message.', telegram_err.message)