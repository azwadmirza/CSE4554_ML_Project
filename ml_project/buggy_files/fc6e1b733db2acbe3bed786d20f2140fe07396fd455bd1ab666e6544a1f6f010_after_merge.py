    def run(self):
        import salt.utils
        salt.utils.warn_until(
            'Nitrogen',
            'Please stop calling \'SaltAPI.run()\' and instead call '
            '\'SaltAPI.start()\'. \'SaltAPI.run()\' will be supported '
            'until Salt {version}.'
        )
        self.start()