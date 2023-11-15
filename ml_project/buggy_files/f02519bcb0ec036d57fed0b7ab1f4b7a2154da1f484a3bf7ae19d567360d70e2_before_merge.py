    async def copy_room_tags_and_direct_to_room(
        self, old_room_id, new_room_id, user_id
    ) -> None:
        """Copies the tags and direct room state from one room to another.

        Args:
            old_room_id: The room ID of the old room.
            new_room_id: The room ID of the new room.
            user_id: The user's ID.
        """
        # Retrieve user account data for predecessor room
        user_account_data, _ = await self.store.get_account_data_for_user(user_id)

        # Copy direct message state if applicable
        direct_rooms = user_account_data.get("m.direct", {})

        # Check which key this room is under
        if isinstance(direct_rooms, dict):
            for key, room_id_list in direct_rooms.items():
                if old_room_id in room_id_list and new_room_id not in room_id_list:
                    # Add new room_id to this key
                    direct_rooms[key].append(new_room_id)

                    # Save back to user's m.direct account data
                    await self.store.add_account_data_for_user(
                        user_id, "m.direct", direct_rooms
                    )
                    break

        # Copy room tags if applicable
        room_tags = await self.store.get_tags_for_room(user_id, old_room_id)

        # Copy each room tag to the new room
        for tag, tag_content in room_tags.items():
            await self.store.add_tag_to_room(user_id, new_room_id, tag, tag_content)