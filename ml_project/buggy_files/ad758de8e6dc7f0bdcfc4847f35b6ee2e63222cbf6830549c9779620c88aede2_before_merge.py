    def list_bots(self):
        if self.args.type == 'text':
            for bot_id in sorted(self.startup.keys()):
                print("Bot ID: {}\nDescription: {}"
                      "".format(bot_id, self.startup[bot_id]['description']))
        return [{'id': bot_id,
                 'description': self.startup[bot_id]['description']}
                for bot_id in sorted(self.startup.keys())]