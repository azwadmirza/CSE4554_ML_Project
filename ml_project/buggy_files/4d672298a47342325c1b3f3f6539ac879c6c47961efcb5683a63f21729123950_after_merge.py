    def pull(self, insecure_registry=False):
        if 'image' not in self.options:
            return

        repo, tag = parse_repository_tag(self.options['image'])
        tag = tag or 'latest'
        log.info('Pulling %s (%s:%s)...' % (self.name, repo, tag))
        output = self.client.pull(
            repo,
            tag=tag,
            stream=True,
            insecure_registry=insecure_registry)
        stream_output(output, sys.stdout)