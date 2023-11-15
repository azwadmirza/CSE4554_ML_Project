    def connectionMade(self):

        message = 'Attached {}@{}'.format(
                   self.ursula.checksum_address,
                   self.ursula.rest_url())

        self.emitter.echo(message, color='green')
        self.emitter.echo('{} | {}'.format(self.ursula.nickname_icon, self.ursula.nickname), color='blue', bold=True)

        self.emitter.echo("\nType 'help' or '?' for help")
        self.transport.write(self.prompt)