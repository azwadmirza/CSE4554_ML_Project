        def after_login(resp):
            if resp.email is None or resp.email == "":
                flash(as_unicode(self.invalid_login_message), "warning")
                return redirect("login")
            user = self.appbuilder.sm.auth_user_oid(resp.email)
            if user is None:
                flash(as_unicode(self.invalid_login_message), "warning")
                return redirect("login")
            remember_me = False
            if "remember_me" in session:
                remember_me = session["remember_me"]
                session.pop("remember_me", None)

            login_user(user, remember=remember_me)
            return redirect(self.appbuilder.get_url_for_index)