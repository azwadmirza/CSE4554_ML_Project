def track_part(bot, trigger):
    if trigger.nick == bot.nick:
        bot.channels.remove(trigger.sender)
        del bot.privileges[trigger.sender]
    else:
        del bot.privileges[trigger.sender][trigger.nick]