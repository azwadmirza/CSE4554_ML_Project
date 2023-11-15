    def closer(request=request): # keep request alive via this function default
        app.threadlocal_manager.pop()