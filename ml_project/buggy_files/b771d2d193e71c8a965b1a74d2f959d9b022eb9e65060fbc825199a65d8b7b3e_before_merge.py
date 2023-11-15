    async def stop(self):
        if self.process and self.process.returncode is None:
            self.process.terminate()