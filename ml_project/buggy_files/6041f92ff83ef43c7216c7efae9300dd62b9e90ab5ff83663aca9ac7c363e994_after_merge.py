    def onLinkCreate(self, link, topology_id, client_id):
        logger.debug("Link created %s", link)
        device_map = dict(Device.objects
                                .filter(topology_id=topology_id, cid__in=[link['from_device_id'], link['to_device_id']])
                                .values_list('cid', 'pk'))
        if link['from_device_id'] not in device_map:
            logger.warning('Device not found')
            return
        if link['to_device_id'] not in device_map:
            logger.warning('Device not found')
            return
        Link.objects.get_or_create(cid=link['id'],
                                   name=link['name'],
                                   from_device_id=device_map[link['from_device_id']],
                                   to_device_id=device_map[link['to_device_id']],
                                   from_interface_id=Interface.objects.get(device_id=device_map[link['from_device_id']],
                                                                           cid=link['from_interface_id']).pk,
                                   to_interface_id=Interface.objects.get(device_id=device_map[link['to_device_id']],
                                                                         cid=link['to_interface_id']).pk)
        (Topology.objects
                 .filter(pk=topology_id, link_id_seq__lt=link['id'])
                 .update(link_id_seq=link['id']))