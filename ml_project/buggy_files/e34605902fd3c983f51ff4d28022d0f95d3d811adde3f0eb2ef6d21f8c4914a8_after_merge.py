    async def start(self):
        # The environment passed into Popen must include SYSTEMROOT, otherwise Popen will fail when called
        # inside python during initialization if %PATH% is configured, but without %SYSTEMROOT%.
        env = {'SYSTEMROOT': os.environ['SYSTEMROOT']} if sys.platform.lower().startswith('win') else {}
        if self.is_app:
            self.process = subprocess.Popen(
                [sys.executable, '-m', 'uvicorn', '--port', _app_port, f'examples.{self.name}:main'],
                env=dict(H2O_WAVE_EXTERNAL_ADDRESS=f'http://{_app_host}:{_app_port}', **env))
        else:
            self.process = subprocess.Popen([sys.executable, os.path.join(example_dir, self.filename)], env=env)