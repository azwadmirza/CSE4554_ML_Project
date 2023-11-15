    async def create_stream(self, file_path: str, key: Optional[bytes] = None,
                            iv_generator: Optional[typing.Generator[bytes, None, None]] = None) -> ManagedStream:
        stream = await ManagedStream.create(self.loop, self.config, self.blob_manager, file_path, key, iv_generator)
        self.streams[stream.sd_hash] = stream
        self.storage.content_claim_callbacks[stream.stream_hash] = lambda: self._update_content_claim(stream)
        if self.config.reflect_streams and self.config.reflector_servers:
            self.reflect_stream(stream)
        return stream