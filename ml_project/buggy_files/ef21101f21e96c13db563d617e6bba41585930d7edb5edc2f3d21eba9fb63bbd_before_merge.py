    def _package_rpc(self):
        parameter = [self.text, self.lang, self.speed, "null"]
        escaped_parameter = json.dumps(parameter, separators=(',', ':'))

        rpc = [[[self.GOOGLE_TTS_RPC, escaped_parameter, None, "generic"]]]
        espaced_rpc = json.dumps(rpc, separators=(',', ':'))
        return "f.req={}&".format(quote(espaced_rpc))