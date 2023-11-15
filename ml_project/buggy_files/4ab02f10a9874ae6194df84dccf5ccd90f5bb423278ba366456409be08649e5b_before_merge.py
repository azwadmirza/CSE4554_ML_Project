    async def delete_stream(self, stream: ManagedStream, delete_file: Optional[bool] = False):
        stream.stop_tasks()
        if stream.sd_hash in self.streams:
            del self.streams[stream.sd_hash]
        blob_hashes = [stream.sd_hash] + [b.blob_hash for b in stream.descriptor.blobs[:-1]]
        await self.blob_manager.delete_blobs(blob_hashes, delete_from_db=False)
        await self.storage.delete_stream(stream.descriptor)
        if delete_file and stream.output_file_exists:
            os.remove(stream.full_path)