    def dispatch(self, request, *args, **kwargs):
        response = super(CompleteView, self).dispatch(request, *args, **kwargs)
        if self.request.user and self.request.user.is_authenticated():
            logger.info(smart_text(u"User {} logged in".format(self.request.user.username)))
            response.set_cookie('userLoggedIn', 'true')
            current_user = UserSerializer(self.request.user)
            current_user = JSONRenderer().render(current_user.data)
            current_user = urllib.quote('%s' % current_user, '')
            response.set_cookie('current_user', current_user)
        return response