    def convert_completion_request(self, response):
        spyder_completions = []
        if response is not None:
            completions = response['completions']
            if completions is not None:
                for completion in completions:
                    entry = {
                        'kind': KITE_DOCUMENT_TYPES.get(
                            completion['hint'], CompletionItemKind.TEXT),
                        'insertText': completion['snippet']['text'],
                        'filterText': completion['display'],
                        'sortText': completion['display'][0],
                        'documentation': completion['documentation']['text']
                    }
                    spyder_completions.append(entry)
        return {'params': spyder_completions}