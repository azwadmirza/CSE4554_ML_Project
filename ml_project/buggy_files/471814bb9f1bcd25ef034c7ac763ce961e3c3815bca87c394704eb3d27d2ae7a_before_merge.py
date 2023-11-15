    def _broadcast_worker(self) -> None:
        def _broadcast(room_name: str, serialized_message: str) -> None:
            if not any(suffix in room_name for suffix in self._config.broadcast_rooms):
                raise RuntimeError(
                    f'Broadcast called on non-public room "{room_name}". '
                    f"Known public rooms: {self._config.broadcast_rooms}."
                )
            room_name = make_room_alias(self.chain_id, room_name)
            if room_name not in self._broadcast_rooms:
                room = join_broadcast_room(self._client, f"#{room_name}:{self._server_name}")
                self._broadcast_rooms[room_name] = room

            existing_room = self._broadcast_rooms.get(room_name)
            assert existing_room, f"Unknown broadcast room: {room_name!r}"

            self.log.debug(
                "Broadcast",
                room_name=room_name,
                room=existing_room,
                data=serialized_message.replace("\n", "\\n"),
            )
            existing_room.send_text(serialized_message)

        while not self._stop_event.ready():
            self._broadcast_event.clear()
            messages: Dict[str, List[Message]] = defaultdict(list)
            while self._broadcast_queue.qsize() > 0:
                room_name, message = self._broadcast_queue.get()
                messages[room_name].append(message)
            for room_name, messages_for_room in messages.items():
                message_text = "\n".join(
                    MessageSerializer.serialize(message) for message in messages_for_room
                )
                _broadcast(room_name, message_text)
                for _ in messages_for_room:
                    # Every message needs to be marked as done.
                    # Unfortunately there's no way to do that in one call :(
                    # https://github.com/gevent/gevent/issues/1436
                    self._broadcast_queue.task_done()

            # Stop prioritizing broadcast messages after initial queue has been emptied
            self._prioritize_broadcast_messages = False
            self._broadcast_event.wait(self._config.retry_interval)