    def connectionMade(self):
        self.emitter.echo("\nType 'help' or '?' for help")
        self.transport.write(self.prompt)