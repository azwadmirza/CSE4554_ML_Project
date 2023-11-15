    async def _process_and_notify(self, stream_name, instance_name, token, rows):
        try:
            if self.send_handler:
                await self.send_handler.process_replication_rows(
                    stream_name, token, rows
                )

            if stream_name == PushRulesStream.NAME:
                self.notifier.on_new_event(
                    "push_rules_key", token, users=[row.user_id for row in rows]
                )
            elif stream_name in (AccountDataStream.NAME, TagAccountDataStream.NAME):
                self.notifier.on_new_event(
                    "account_data_key", token, users=[row.user_id for row in rows]
                )
            elif stream_name == ReceiptsStream.NAME:
                self.notifier.on_new_event(
                    "receipt_key", token, rooms=[row.room_id for row in rows]
                )
                await self.pusher_pool.on_new_receipts(
                    token, token, {row.room_id for row in rows}
                )
            elif stream_name == TypingStream.NAME:
                self.typing_handler.process_replication_rows(token, rows)
                self.notifier.on_new_event(
                    "typing_key", token, rooms=[row.room_id for row in rows]
                )
            elif stream_name == ToDeviceStream.NAME:
                entities = [row.entity for row in rows if row.entity.startswith("@")]
                if entities:
                    self.notifier.on_new_event("to_device_key", token, users=entities)
            elif stream_name == DeviceListsStream.NAME:
                all_room_ids = set()
                for row in rows:
                    if row.entity.startswith("@"):
                        room_ids = await self.store.get_rooms_for_user(row.entity)
                        all_room_ids.update(room_ids)
                self.notifier.on_new_event("device_list_key", token, rooms=all_room_ids)
            elif stream_name == PresenceStream.NAME:
                await self.presence_handler.process_replication_rows(token, rows)
            elif stream_name == GroupServerStream.NAME:
                self.notifier.on_new_event(
                    "groups_key", token, users=[row.user_id for row in rows]
                )
            elif stream_name == PushersStream.NAME:
                for row in rows:
                    if row.deleted:
                        self.stop_pusher(row.user_id, row.app_id, row.pushkey)
                    else:
                        await self.start_pusher(row.user_id, row.app_id, row.pushkey)
        except Exception:
            logger.exception("Error processing replication")