    def gather_default(self, req_type, responses):
        response = ''
        for source in self.SOURCE_PRIORITY[req_type]:
            if source in responses:
                response = responses[source].get('params', '')
                if response:
                    break
        return {'params': response}