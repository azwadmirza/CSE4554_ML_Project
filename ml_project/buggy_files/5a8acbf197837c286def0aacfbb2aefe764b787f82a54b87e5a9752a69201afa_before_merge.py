    def _is_broadcast_room(self, room: Room) -> bool:
        return any(
            suffix in room_alias
            for suffix in self._config.broadcast_rooms
            for room_alias in room.aliases
        )