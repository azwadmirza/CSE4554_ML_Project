    def determine_actions(self, request, view):
        actions = super(SublistAttachDetatchMetadata, self).determine_actions(request, view)
        method = 'POST'
        if method in actions:
            for field in list(actions[method].keys()):
                if field == 'id':
                    continue
                actions[method].pop(field)
        return actions