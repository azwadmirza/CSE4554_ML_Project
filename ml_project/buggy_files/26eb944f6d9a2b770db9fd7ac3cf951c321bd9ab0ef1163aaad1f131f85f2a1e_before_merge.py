    def set_cookie(
        cls,
        message,
        key,
        value="",
        max_age=None,
        expires=None,
        path="/",
        domain=None,
        secure=False,
        httponly=False,
    ):
        """
        Sets a cookie in the passed HTTP response message.

        ``expires`` can be:
        - a string in the correct format,
        - a naive ``datetime.datetime`` object in UTC,
        - an aware ``datetime.datetime`` object in any time zone.
        If it is a ``datetime.datetime`` object then ``max_age`` will be calculated.
        """
        value = force_str(value)
        cookies = SimpleCookie()
        cookies[key] = value
        if expires is not None:
            if isinstance(expires, datetime.datetime):
                if timezone.is_aware(expires):
                    expires = timezone.make_naive(expires, timezone.utc)
                delta = expires - expires.utcnow()
                # Add one second so the date matches exactly (a fraction of
                # time gets lost between converting to a timedelta and
                # then the date string).
                delta = delta + datetime.timedelta(seconds=1)
                # Just set max_age - the max_age logic will set expires.
                expires = None
                max_age = max(0, delta.days * 86400 + delta.seconds)
            else:
                cookies[key]["expires"] = expires
        else:
            cookies[key]["expires"] = ""
        if max_age is not None:
            cookies[key]["max-age"] = max_age
            # IE requires expires, so set it if hasn't been already.
            if not expires:
                cookies[key]["expires"] = cookie_date(time.time() + max_age)
        if path is not None:
            cookies[key]["path"] = path
        if domain is not None:
            cookies[key]["domain"] = domain
        if secure:
            cookies[key]["secure"] = True
        if httponly:
            cookies[key]["httponly"] = True
        # Write out the cookies to the response
        for c in cookies.values():
            message.setdefault("headers", []).append(
                (b"Set-Cookie", bytes(c.output(header=""), encoding="utf-8"))
            )