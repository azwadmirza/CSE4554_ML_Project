def auth_proceed(bot, trigger):
    if trigger.args[0] != '+':
        # How did we get here? I am not good with computer.
        return
    # Is this right?
    if bot.config.core.sasl_username:
        sasl_username = bot.config.core.sasl_username
    else:
        sasl_username = bot.nick
    sasl_token = '\0'.join((sasl_username, sasl_username,
                           bot.config.core.sasl_password))
    # Spec says we do a base 64 encode on the SASL stuff
    bot.write(('AUTHENTICATE', base64.b64encode(sasl_token)))