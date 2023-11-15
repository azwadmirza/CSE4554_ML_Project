    def login(self, flag=True):
        @self.appbuilder.sm.oid.loginhandler
        def login_handler(self):
            if g.user is not None and g.user.is_authenticated:
                return redirect(self.appbuilder.get_url_for_index)
            form = LoginForm_oid()
            if form.validate_on_submit():
                session["remember_me"] = form.remember_me.data
                return self.appbuilder.sm.oid.try_login(
                    form.openid.data,
                    ask_for=self.oid_ask_for,
                    ask_for_optional=self.oid_ask_for_optional,
                )
            return self.render_template(
                self.login_template,
                title=self.title,
                form=form,
                providers=self.appbuilder.sm.openid_providers,
                appbuilder=self.appbuilder,
            )

        @self.appbuilder.sm.oid.after_login
        def after_login(resp):
            if resp.email is None or resp.email == "":
                flash(as_unicode(self.invalid_login_message), "warning")
                return redirect(self.appbuilder.get_url_for_login)
            user = self.appbuilder.sm.auth_user_oid(resp.email)
            if user is None:
                flash(as_unicode(self.invalid_login_message), "warning")
                return redirect(self.appbuilder.get_url_for_login)
            remember_me = False
            if "remember_me" in session:
                remember_me = session["remember_me"]
                session.pop("remember_me", None)

            login_user(user, remember=remember_me)
            return redirect(self.appbuilder.get_url_for_index)

        return login_handler(self)