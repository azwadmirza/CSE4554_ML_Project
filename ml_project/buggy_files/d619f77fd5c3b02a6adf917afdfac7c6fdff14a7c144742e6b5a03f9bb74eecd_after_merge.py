    async def get_user_directory_stream_pos(self) -> Optional[int]:
        """
        Get the stream ID of the user directory stream.

        Returns:
            The stream token or None if the initial background update hasn't happened yet.
        """
        return await self.db_pool.simple_select_one_onecol(
            table="user_directory_stream_pos",
            keyvalues={},
            retcol="stream_id",
            desc="get_user_directory_stream_pos",
        )