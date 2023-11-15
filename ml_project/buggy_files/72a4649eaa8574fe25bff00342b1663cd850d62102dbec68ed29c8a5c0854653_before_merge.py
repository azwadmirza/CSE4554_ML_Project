    def handle(self, *args: Any, **options: str) -> None:
        if settings.STAGING:
            print('This is a Staging server. Suppressing management command.')
            sys.exit(0)

        realm = self.get_realm(options)
        user_emails = options['users']  # type: ignore  # mypy thinks this is a str, not List[str] #
        activate = options['activate']
        deactivate = options['deactivate']

        filter_kwargs = {}  # type: Dict[str, Realm]
        if realm is not None:
            filter_kwargs = dict(realm=realm)

        if activate:
            if not user_emails:
                print('You need to specify at least one user to use the activate option.')
                self.print_help("./manage.py", "soft_deactivate_users")
                sys.exit(1)

            users_to_activate = get_users_from_emails(user_emails, filter_kwargs)
            users_activated = do_soft_activate_users(users_to_activate)
            logger.info('Soft Reactivated %d user(s)' % (len(users_activated)))

        elif deactivate:
            if user_emails:
                users_to_deactivate = get_users_from_emails(user_emails, filter_kwargs)
                print('Soft deactivating forcefully...')
            else:
                if realm is not None:
                    filter_kwargs = dict(user_profile__realm=realm)
                users_to_deactivate = get_users_for_soft_deactivation(int(options['inactive_for']),
                                                                      filter_kwargs)

            if users_to_deactivate:
                users_deactivated = do_soft_deactivate_users(users_to_deactivate)
                logger.info('Soft Deactivated %d user(s)' % (len(users_deactivated)))
        else:
            self.print_help("./manage.py", "soft_deactivate_users")
            sys.exit(1)