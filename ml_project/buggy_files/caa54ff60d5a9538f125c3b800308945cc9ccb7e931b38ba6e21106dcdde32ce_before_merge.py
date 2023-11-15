    def run(self):
        """Run manual snatch job."""
        generic_queue.QueueItem.run(self)
        self.started = True

        result = providers.get_provider_class(self.provider).get_result(self.segment)
        result.series = self.show
        result.url = self.cached_result[b'url']
        result.quality = int(self.cached_result[b'quality'])
        result.name = self.cached_result[b'name']
        result.size = int(self.cached_result[b'size'])
        result.seeders = int(self.cached_result[b'seeders'])
        result.leechers = int(self.cached_result[b'leechers'])
        result.release_group = self.cached_result[b'release_group']
        result.version = int(self.cached_result[b'version'])
        result.proper_tags = self.cached_result[b'proper_tags'].split('|') \
            if self.cached_result[b'proper_tags'] else ''
        result.manually_searched = True

        try:
            log.info('Beginning to manual snatch release: {name}',
                     {'name': result.name})

            if result:
                if result.seeders not in (-1, None) and result.leechers not in (-1, None):
                    log.info(
                        'Downloading {name} with {seeders} seeders and {leechers} leechers'
                        ' and size {size} from {provider}', {
                            'name': result.name,
                            'seeders': result.seeders,
                            'leechers': result.leechers,
                            'size': pretty_file_size(result.size),
                            'provider': result.provider.name,
                        }
                    )
                else:
                    log.info(
                        'Downloading {name} with size: {size} from {provider}', {
                            'name': result.name,
                            'size': pretty_file_size(result.size),
                            'provider': result.provider.name,
                        }
                    )
                self.success = snatch_episode(result)
            else:
                log.info('Unable to snatch release: {name}',
                         {'name': result.name})

            # give the CPU a break
            time.sleep(common.cpu_presets[app.CPU_PRESET])

        except Exception:
            self.success = False
            log.exception('Manual snatch failed!. For result: {name}', {'name': result.name})
            ui.notifications.message('Error while snatching selected result',
                                     'Unable to snatch the result for <i>{name}</i>'.format(name=result.name))

        if self.success is None:
            self.success = False

        self.finish()