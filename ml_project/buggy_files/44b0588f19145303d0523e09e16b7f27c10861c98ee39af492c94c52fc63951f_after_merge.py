    def process_hover(self, response):
        logger.debug(response)
        if response is not None:
            report = response['report']
            text = report['description_text']
            if len(text) == 0:
                text = None
        else:
            text = None

        return {'params': text}