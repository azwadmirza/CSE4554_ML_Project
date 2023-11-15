    def process_hover(self, response):
        # logger.debug(response)
        report = response['report']
        text = report['description_text']
        if len(text) == 0:
            text = None
        return {'params': text}