    def _is_broadcast_room(self, room: Room) -> bool:
        room_aliases = set(room.aliases)
        if room.canonical_alias:
            room_aliases.add(room.canonical_alias)
        return any(
            suffix in room_alias
            for suffix in self._config.broadcast_rooms
            for room_alias in room.aliases
        )