    def dispatch(self, request, *args, **kwargs):
        response = super(CompleteView, self).dispatch(request, *args, **kwargs)
        if self.request.user and self.request.user.is_authenticated():
            auth.login(self.request, self.request.user)
            logger.info(smart_text(u"User {} logged in".format(self.request.user.username)))
        return response