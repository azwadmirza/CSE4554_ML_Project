    def init_spawners(self):
        db = self.db

        user_summaries = ['']

        def _user_summary(user):
            parts = ['{0: >8}'.format(user.name)]
            if user.admin:
                parts.append('admin')
            for name, spawner in sorted(user.spawners.items(), key=itemgetter(0)):
                if spawner.server:
                    parts.append('%s:%s running at %s' % (user.name, name, spawner.server))
            return ' '.join(parts)

        @gen.coroutine
        def user_stopped(user, server_name):
            spawner = user.spawners[server_name]
            status = yield spawner.poll()
            self.log.warning("User %s server stopped with exit code: %s",
                user.name, status,
            )
            yield self.proxy.delete_user(user, server_name)
            yield user.stop(server_name)

        for orm_user in db.query(orm.User):
            self.users[orm_user.id] = user = User(orm_user, self.tornado_settings)
            self.log.debug("Loading state for %s from db", user.name)
            for name, spawner in user.spawners.items():
                status = 0
                if spawner.server:
                    try:
                        status = yield spawner.poll()
                    except Exception:
                        self.log.exception("Failed to poll spawner for %s, assuming the spawner is not running.",
                            spawner._log_name)
                        status = -1

                if status is None:
                    self.log.info("%s still running", user.name)
                    spawner.add_poll_callback(user_stopped, user, name)
                    spawner.start_polling()
                else:
                    # user not running. This is expected if server is None,
                    # but indicates the user's server died while the Hub wasn't running
                    # if spawner.server is defined.
                    if spawner.server:
                        self.log.warning("%s appears to have stopped while the Hub was down", spawner._log_name)
                        # remove server entry from db
                        db.delete(spawner.orm_spawner.server)
                        spawner.server = None
                    else:
                        self.log.debug("%s not running", spawner._log_name)
            db.commit()

            user_summaries.append(_user_summary(user))

        self.log.debug("Loaded users: %s", '\n'.join(user_summaries))
        db.commit()