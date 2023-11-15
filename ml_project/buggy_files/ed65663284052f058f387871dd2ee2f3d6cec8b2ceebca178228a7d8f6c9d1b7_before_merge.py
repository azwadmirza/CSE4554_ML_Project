    def dbb_generate_wallet(self):
        key = self.stretch_key(self.password)
        filename = ("Electrum-" + time.strftime("%Y-%m-%d-%H-%M-%S") + ".pdf")
        msg = ('{"seed":{"source": "create", "key": "%s", "filename": "%s", "entropy": "%s"}}' % (key, filename, 'Digital Bitbox Electrum Plugin')).encode('utf8')
        reply = self.hid_send_encrypt(msg)
        if 'error' in reply:
            raise UserFacingException(reply['error']['message'])