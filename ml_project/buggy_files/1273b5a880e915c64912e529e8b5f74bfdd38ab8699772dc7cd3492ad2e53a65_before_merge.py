    async def resolve_room_id(self, room_identifier: str) -> str:
        """Resolve to a room ID, if necessary."""
        if RoomID.is_valid(room_identifier):
            resolved_room_id = room_identifier
        elif RoomAlias.is_valid(room_identifier):
            room_alias = RoomAlias.from_string(room_identifier)
            room_id, _ = await self.room_member_handler.lookup_room_alias(room_alias)
            resolved_room_id = room_id.to_string()
        else:
            raise SynapseError(
                400, "%s was not legal room ID or room alias" % (room_identifier,)
            )
        if not resolved_room_id:
            raise SynapseError(
                400, "Unknown room ID or room alias %s" % room_identifier
            )
        return resolved_room_id