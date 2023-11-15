def ws_message(message):
    # Send to all clients editing the topology
    channels.Group("topology-%s" % message.channel_session['topology_id']).send({"text": message['text']})
    # Send to networking_events handler
    networking_events_dispatcher.handle({"text": message['text'],
                                         "topology": message.channel_session['topology_id'],
                                         "client": message.channel_session['client_id']})