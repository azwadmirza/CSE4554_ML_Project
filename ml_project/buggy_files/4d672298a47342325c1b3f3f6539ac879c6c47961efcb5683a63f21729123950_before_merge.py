    def pull(self, insecure_registry=False):
        if 'image' in self.options:
            image_name = self._get_image_name(self.options['image'])
            log.info('Pulling %s (%s)...' % (self.name, image_name))
            self.client.pull(
                image_name,
                insecure_registry=insecure_registry
            )