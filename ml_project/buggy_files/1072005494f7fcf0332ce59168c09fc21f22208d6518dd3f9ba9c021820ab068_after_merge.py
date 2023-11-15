    async def send(self, message):
        """
        Overridden send that also does session saves/cookies.
        """
        # Only save session if we're the outermost session middleware
        if self.activated:
            modified = self.scope["session"].modified
            empty = self.scope["session"].is_empty()
            # If this is a message type that we want to save on, and there's
            # changed data, save it. We also save if it's empty as we might
            # not be able to send a cookie-delete along with this message.
            if (
                message["type"] in self.middleware.save_message_types
                and message.get("status", 200) != 500
                and (modified or settings.SESSION_SAVE_EVERY_REQUEST)
            ):
                self.save_session()
                # If this is a message type that can transport cookies back to the
                # client, then do so.
                if message["type"] in self.middleware.cookie_response_message_types:
                    if empty:
                        # Delete cookie if it's set
                        if settings.SESSION_COOKIE_NAME in self.scope["cookies"]:
                            CookieMiddleware.delete_cookie(
                                message,
                                settings.SESSION_COOKIE_NAME,
                                path=settings.SESSION_COOKIE_PATH,
                                domain=settings.SESSION_COOKIE_DOMAIN,
                            )
                    else:
                        # Get the expiry data
                        if self.scope["session"].get_expire_at_browser_close():
                            max_age = None
                            expires = None
                        else:
                            max_age = self.scope["session"].get_expiry_age()
                            expires_time = time.time() + max_age
                            expires = http_date(expires_time)
                        # Set the cookie
                        CookieMiddleware.set_cookie(
                            message,
                            self.middleware.cookie_name,
                            self.scope["session"].session_key,
                            max_age=max_age,
                            expires=expires,
                            domain=settings.SESSION_COOKIE_DOMAIN,
                            path=settings.SESSION_COOKIE_PATH,
                            secure=settings.SESSION_COOKIE_SECURE or None,
                            httponly=settings.SESSION_COOKIE_HTTPONLY or None,
                        )
        # Pass up the send
        return await self.real_send(message)