    def get_new_session(self) -> aiohttp.ClientSession:
        return aiohttp.ClientSession(
            connector=self._connector_class(**self._connector_init, loop=self._main_loop),
            loop=self._main_loop,
            json_serialize=json.dumps
        )