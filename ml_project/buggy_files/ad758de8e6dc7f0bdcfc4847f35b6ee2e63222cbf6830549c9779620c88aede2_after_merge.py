    def list_bots(self):
        """
        Lists all configured bots from startup.conf with bot id and
        description.

        If description is not set, None is used instead.
        """
        if self.args.type == 'text':
            for bot_id in sorted(self.startup.keys()):
                print("Bot ID: {}\nDescription: {}"
                      "".format(bot_id, self.startup[bot_id].get('description')))
        return [{'id': bot_id,
                 'description': self.startup[bot_id].get('description')}
                for bot_id in sorted(self.startup.keys())]