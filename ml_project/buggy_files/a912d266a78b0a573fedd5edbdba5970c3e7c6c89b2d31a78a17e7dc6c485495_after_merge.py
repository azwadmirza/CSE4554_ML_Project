def ws_connect(message):
    if not message.user.is_authenticated():
        logger.error("Request user is not authenticated to use websocket.")
        message.reply_channel.send({"close": True})
        return
    else:
        message.reply_channel.send({"accept": True})

    data = urlparse.parse_qs(message.content['query_string'])
    inventory_id = parse_inventory_id(data)
    topology_ids = list(TopologyInventory.objects.filter(inventory_id=inventory_id).values_list('pk', flat=True))
    topology_id = None
    if len(topology_ids) > 0:
        topology_id = topology_ids[0]
    if topology_id is not None:
        topology = Topology.objects.get(pk=topology_id)
    else:
        topology = Topology(name="topology", scale=1.0, panX=0, panY=0)
        topology.save()
        TopologyInventory(inventory_id=inventory_id, topology_id=topology.pk).save()
    topology_id = topology.pk
    message.channel_session['topology_id'] = topology_id
    channels.Group("topology-%s" % topology_id).add(message.reply_channel)
    client = Client()
    client.save()
    message.channel_session['client_id'] = client.pk
    channels.Group("client-%s" % client.pk).add(message.reply_channel)
    message.reply_channel.send({"text": json.dumps(["id", client.pk])})
    message.reply_channel.send({"text": json.dumps(["topology_id", topology_id])})
    topology_data = transform_dict(dict(id='topology_id',
                                        name='name',
                                        panX='panX',
                                        panY='panY',
                                        scale='scale',
                                        link_id_seq='link_id_seq',
                                        device_id_seq='device_id_seq'), topology.__dict__)

    message.reply_channel.send({"text": json.dumps(["Topology", topology_data])})
    send_snapshot(message.reply_channel, topology_id)