    def onLinkDestroy(self, link, topology_id, client_id):
        logger.debug("Link deleted %s", link)
        device_map = dict(Device.objects
                                .filter(topology_id=topology_id, cid__in=[link['from_device_id'], link['to_device_id']])
                                .values_list('cid', 'pk'))
        if link['from_device_id'] not in device_map:
            return
        if link['to_device_id'] not in device_map:
            return
        Link.objects.filter(cid=link['id'],
                            from_device_id=device_map[link['from_device_id']],
                            to_device_id=device_map[link['to_device_id']],
                            from_interface_id=Interface.objects.get(device_id=device_map[link['from_device_id']],
                                                                    cid=link['from_interface_id']).pk,
                            to_interface_id=Interface.objects.get(device_id=device_map[link['to_device_id']],
                                                                  cid=link['to_interface_id']).pk).delete()