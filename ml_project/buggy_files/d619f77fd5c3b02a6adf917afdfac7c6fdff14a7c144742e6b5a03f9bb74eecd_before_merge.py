    async def get_user_directory_stream_pos(self) -> int:
        return await self.db_pool.simple_select_one_onecol(
            table="user_directory_stream_pos",
            keyvalues={},
            retcol="stream_id",
            desc="get_user_directory_stream_pos",
        )