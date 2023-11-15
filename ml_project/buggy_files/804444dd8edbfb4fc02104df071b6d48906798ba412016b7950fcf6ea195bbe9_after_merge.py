    def getTraktToken(trakt_pin=None):
        trakt_settings = {"trakt_api_key": app.TRAKT_API_KEY,
                          "trakt_api_secret": app.TRAKT_API_SECRET}
        trakt_api = TraktApi(app.SSL_VERIFY, app.TRAKT_TIMEOUT, **trakt_settings)
        response = None
        try:
            (access_token, refresh_token) = trakt_api.get_token(app.TRAKT_REFRESH_TOKEN, trakt_pin=trakt_pin)
            if access_token and refresh_token:
                app.TRAKT_ACCESS_TOKEN = access_token
                app.TRAKT_REFRESH_TOKEN = refresh_token
                response = trakt_api.validate_account()
        except MissingTokenException:
            ui.notifications.error('You need to get a PIN and authorize Medusa app')
            return 'You need to get a PIN and authorize Medusa app'
        except TokenExpiredException:
            # Clear existing tokens
            app.TRAKT_ACCESS_TOKEN = ''
            app.TRAKT_REFRESH_TOKEN = ''
            ui.notifications.error('TOKEN expired. Reload page, get a new PIN and authorize Medusa app')
            return 'TOKEN expired. Reload page, get a new PIN and authorize Medusa app'
        except TraktException:
            ui.notifications.error("Connection error. Click 'Authorize Medusa' button again")
            return "Connection error. Click 'Authorize Medusa' button again"
        if response:
            ui.notifications.message('Trakt Authorized')
            return "Trakt Authorized"
        ui.notifications.error('Connection error. Reload the page to get new token!')
        return "Trakt Not Authorized!"