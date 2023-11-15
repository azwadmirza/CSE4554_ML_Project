    def commit(self, comment=None, label=None):
        if comment and label:
            command = 'commit label {0} comment {1}'.format(label, comment)
        elif comment:
            command = 'commit comment {0}'.format(comment)
        elif label:
            command = 'commit label {0}'.format(label)
        else:
            command = 'commit'
        self.send_command(command)