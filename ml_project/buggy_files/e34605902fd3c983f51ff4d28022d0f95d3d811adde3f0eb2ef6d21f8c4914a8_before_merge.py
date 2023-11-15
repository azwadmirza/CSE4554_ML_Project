    async def start(self):
        if self.is_app:
            self.process = await asyncio.create_subprocess_exec(
                sys.executable, '-m', 'uvicorn', '--port', _app_port, f'examples.{self.name}:main', env=dict(
                    H2O_WAVE_EXTERNAL_ADDRESS=f'http://{_app_host}:{_app_port}'
                ),
            )
        else:
            self.process = await asyncio.create_subprocess_exec(
                sys.executable, os.path.join(example_dir, self.filename)
            )