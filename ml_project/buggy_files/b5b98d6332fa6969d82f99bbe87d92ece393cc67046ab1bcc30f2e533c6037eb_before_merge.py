def ws_disconnect(message):
    if 'topology_id' in message.channel_session:
        Group("topology-%s" % message.channel_session['topology_id']).discard(message.reply_channel)