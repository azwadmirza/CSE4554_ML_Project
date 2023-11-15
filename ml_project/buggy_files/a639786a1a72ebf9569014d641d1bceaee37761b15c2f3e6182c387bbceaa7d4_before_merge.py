    def ask_passwords(self):
        ''' prompt for connection and become passwords if needed '''

        op = self.options
        sshpass = None
        becomepass = None
        become_prompt = ''

        if op.ask_pass:
            sshpass = getpass.getpass(prompt="SSH password: ")
            become_prompt = "%s password[defaults to SSH password]: " % op.become_method.upper()
            if sshpass:
                sshpass = to_bytes(sshpass, errors='strict', nonstring='simplerepr')
        else:
            become_prompt = "%s password: " % op.become_method.upper()

        if op.become_ask_pass:
            becomepass = getpass.getpass(prompt=become_prompt)
            if op.ask_pass and becomepass == '':
                becomepass = sshpass
            if becomepass:
                becomepass = to_bytes(becomepass)

        return (sshpass, becomepass)