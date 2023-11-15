    async def notify_device_update(self, user_id, device_ids):
        """Notify that a user's device(s) has changed. Pokes the notifier, and
        remote servers if the user is local.
        """
        if not device_ids:
            # No changes to notify about, so this is a no-op.
            return

        users_who_share_room = await self.store.get_users_who_share_room_with_user(
            user_id
        )

        hosts = set()
        if self.hs.is_mine_id(user_id):
            hosts.update(get_domain_from_id(u) for u in users_who_share_room)
            hosts.discard(self.server_name)

        set_tag("target_hosts", hosts)

        position = await self.store.add_device_change_to_streams(
            user_id, device_ids, list(hosts)
        )

        if not position:
            # This should only happen if there are no updates, so we bail.
            return

        for device_id in device_ids:
            logger.debug(
                "Notifying about update %r/%r, ID: %r", user_id, device_id, position
            )

        room_ids = await self.store.get_rooms_for_user(user_id)

        # specify the user ID too since the user should always get their own device list
        # updates, even if they aren't in any rooms.
        self.notifier.on_new_event(
            "device_list_key", position, users=[user_id], rooms=room_ids
        )

        if hosts:
            logger.info(
                "Sending device list update notif for %r to: %r", user_id, hosts
            )
            for host in hosts:
                self.federation_sender.send_device_messages(host)
                log_kv({"message": "sent device update to host", "host": host})