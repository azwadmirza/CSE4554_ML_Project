    def gather_default(self, req_type, responses):
        response = None
        for source in self.SOURCE_PRIORITY[req_type]:
            if source in responses:
                response = responses[source].get('params', None)
                if response:
                    break
        return {'params': response}