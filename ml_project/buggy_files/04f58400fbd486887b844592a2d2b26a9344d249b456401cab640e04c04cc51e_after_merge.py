    def handle(self, **options: Any) -> None:
        if options["percent_huddles"] + options["percent_personals"] > 100:
            self.stderr.write("Error!  More than 100% of messages allocated.\n")
            return

        if options["delete"]:
            # Start by clearing all the data in our database
            clear_database()

            # Create our two default realms
            # Could in theory be done via zerver.lib.actions.do_create_realm, but
            # welcome-bot (needed for do_create_realm) hasn't been created yet
            zulip_realm = Realm.objects.create(
                string_id="zulip", name="Zulip Dev", restricted_to_domain=True,
                description="The Zulip development environment default organization."
                            "  It's great for testing!",
                invite_required=False, org_type=Realm.CORPORATE)
            RealmDomain.objects.create(realm=zulip_realm, domain="zulip.com")
            if options["test_suite"]:
                mit_realm = Realm.objects.create(
                    string_id="zephyr", name="MIT", restricted_to_domain=True,
                    invite_required=False, org_type=Realm.CORPORATE)
                RealmDomain.objects.create(realm=mit_realm, domain="mit.edu")

                lear_realm = Realm.objects.create(
                    string_id="lear", name="Lear & Co.", restricted_to_domain=False,
                    invite_required=False, org_type=Realm.CORPORATE)

            # Create test Users (UserProfiles are automatically created,
            # as are subscriptions to the ability to receive personals).
            names = [
                ("Zoe", "ZOE@zulip.com"),
                ("Othello, the Moor of Venice", "othello@zulip.com"),
                ("Iago", "iago@zulip.com"),
                ("Prospero from The Tempest", "prospero@zulip.com"),
                ("Cordelia Lear", "cordelia@zulip.com"),
                ("King Hamlet", "hamlet@zulip.com"),
                ("aaron", "AARON@zulip.com"),
            ]
            for i in range(options["extra_users"]):
                names.append(('Extra User %d' % (i,), 'extrauser%d@zulip.com' % (i,)))
            create_users(zulip_realm, names)

            iago = get_user("iago@zulip.com", zulip_realm)
            do_change_is_admin(iago, True)
            iago.is_staff = True
            iago.save(update_fields=['is_staff'])

            # These bots are directly referenced from code and thus
            # are needed for the test suite.
            all_realm_bots = [(bot['name'], bot['email_template'] % (settings.INTERNAL_BOT_DOMAIN,))
                              for bot in settings.INTERNAL_BOTS]
            zulip_realm_bots = [
                ("Zulip New User Bot", "new-user-bot@zulip.com"),
                ("Zulip Error Bot", "error-bot@zulip.com"),
                ("Zulip Default Bot", "default-bot@zulip.com"),
                ("Welcome Bot", "welcome-bot@zulip.com"),
            ]

            for i in range(options["extra_bots"]):
                zulip_realm_bots.append(('Extra Bot %d' % (i,), 'extrabot%d@zulip.com' % (i,)))
            zulip_realm_bots.extend(all_realm_bots)
            create_users(zulip_realm, zulip_realm_bots, bot_type=UserProfile.DEFAULT_BOT)

            zoe = get_user("zoe@zulip.com", zulip_realm)
            zulip_webhook_bots = [
                ("Zulip Webhook Bot", "webhook-bot@zulip.com"),
            ]
            # If a stream is not supplied in the webhook URL, the webhook
            # will (in some cases) send the notification as a PM to the
            # owner of the webhook bot, so bot_owner can't be None
            create_users(zulip_realm, zulip_webhook_bots,
                         bot_type=UserProfile.INCOMING_WEBHOOK_BOT, bot_owner=zoe)
            aaron = get_user("AARON@zulip.com", zulip_realm)
            zulip_outgoing_bots = [
                ("Outgoing Webhook", "outgoing-webhook@zulip.com")
            ]
            create_users(zulip_realm, zulip_outgoing_bots,
                         bot_type=UserProfile.OUTGOING_WEBHOOK_BOT, bot_owner=aaron)
            # TODO: Clean up this initial bot creation code
            Service.objects.create(
                name="test",
                user_profile=get_user("outgoing-webhook@zulip.com", zulip_realm),
                base_url="http://127.0.0.1:5002/bots/followup",
                token="abcd1234",
                interface=1)

            # Create public streams.
            stream_list = ["Verona", "Denmark", "Scotland", "Venice", "Rome"]
            stream_dict = {
                "Verona": {"description": "A city in Italy", "invite_only": False},
                "Denmark": {"description": "A Scandinavian country", "invite_only": False},
                "Scotland": {"description": "Located in the United Kingdom", "invite_only": False},
                "Venice": {"description": "A northeastern Italian city", "invite_only": False},
                "Rome": {"description": "Yet another Italian city", "invite_only": False}
            }  # type: Dict[Text, Dict[Text, Any]]

            bulk_create_streams(zulip_realm, stream_dict)
            recipient_streams = [Stream.objects.get(name=name, realm=zulip_realm).id
                                 for name in stream_list]  # type: List[int]
            # Create subscriptions to streams.  The following
            # algorithm will give each of the users a different but
            # deterministic subset of the streams (given a fixed list
            # of users).
            subscriptions_to_add = []  # type: List[Subscription]
            event_time = timezone_now()
            all_subscription_logs = []  # type: (List[RealmAuditLog])
            profiles = UserProfile.objects.select_related().filter(
                is_bot=False).order_by("email")  # type: Sequence[UserProfile]
            for i, profile in enumerate(profiles):
                # Subscribe to some streams.
                for type_id in recipient_streams[:int(len(recipient_streams) *
                                                      float(i)/len(profiles)) + 1]:
                    r = Recipient.objects.get(type=Recipient.STREAM, type_id=type_id)
                    s = Subscription(
                        recipient=r,
                        user_profile=profile,
                        color=STREAM_ASSIGNMENT_COLORS[i % len(STREAM_ASSIGNMENT_COLORS)])

                    subscriptions_to_add.append(s)

                    log = RealmAuditLog(realm=profile.realm,
                                        modified_user=profile,
                                        modified_stream_id=type_id,
                                        event_last_message_id=0,
                                        event_type='subscription_created',
                                        event_time=event_time)
                    all_subscription_logs.append(log)

            Subscription.objects.bulk_create(subscriptions_to_add)
            RealmAuditLog.objects.bulk_create(all_subscription_logs)

            # Create custom profile field data
            phone_number = try_add_realm_custom_profile_field(zulip_realm, "Phone number",
                                                              CustomProfileField.SHORT_TEXT)
            biography = try_add_realm_custom_profile_field(zulip_realm, "Biography",
                                                           CustomProfileField.LONG_TEXT)
            favorite_integer = try_add_realm_custom_profile_field(zulip_realm, "Favorite integer",
                                                                  CustomProfileField.INTEGER)

            # Fill in values for Iago and Hamlet
            hamlet = get_user("hamlet@zulip.com", zulip_realm)
            do_update_user_custom_profile_data(iago, [
                {"id": phone_number.id, "value": "+1-234-567-8901"},
                {"id": biography.id, "value": "Betrayer of Othello."},
                {"id": favorite_integer.id, "value": 17},
            ])
            do_update_user_custom_profile_data(hamlet, [
                {"id": phone_number.id, "value": "+0-11-23-456-7890"},
                {"id": biography.id, "value": "Prince of Denmark, and other things!"},
                {"id": favorite_integer.id, "value": 12},
            ])
        else:
            zulip_realm = get_realm("zulip")
            recipient_streams = [klass.type_id for klass in
                                 Recipient.objects.filter(type=Recipient.STREAM)]

        # Extract a list of all users
        user_profiles = list(UserProfile.objects.filter(is_bot=False))  # type: List[UserProfile]

        # Create a test realm emoji.
        IMAGE_FILE_PATH = os.path.join(settings.STATIC_ROOT, 'images', 'test-images', 'checkbox.png')
        with open(IMAGE_FILE_PATH, 'rb') as fp:
            check_add_realm_emoji(zulip_realm, 'green_tick', iago, fp)

        if not options["test_suite"]:
            # Populate users with some bar data
            for user in user_profiles:
                status = UserPresence.ACTIVE  # type: int
                date = timezone_now()
                client = get_client("website")
                if user.full_name[0] <= 'H':
                    client = get_client("ZulipAndroid")
                UserPresence.objects.get_or_create(user_profile=user,
                                                   client=client,
                                                   timestamp=date,
                                                   status=status)

        user_profiles_ids = [user_profile.id for user_profile in user_profiles]

        # Create several initial huddles
        for i in range(options["num_huddles"]):
            get_huddle(random.sample(user_profiles_ids, random.randint(3, 4)))

        # Create several initial pairs for personals
        personals_pairs = [random.sample(user_profiles_ids, 2)
                           for i in range(options["num_personals"])]

        # Generate a new set of test data.
        create_test_data()

        # prepopulate the URL preview/embed data for the links present
        # in the config.generate_data.json data set.  This makes it
        # possible for populate_db to run happily without Internet
        # access.
        with open("zerver/fixtures/docs_url_preview_data.json", "r") as f:
            urls_with_preview_data = ujson.load(f)
            for url in urls_with_preview_data:
                cache_set(url, urls_with_preview_data[url], PREVIEW_CACHE_NAME)

        threads = options["threads"]
        jobs = []  # type: List[Tuple[int, List[List[int]], Dict[str, Any], Callable[[str], int], int]]
        for i in range(threads):
            count = options["num_messages"] // threads
            if i < options["num_messages"] % threads:
                count += 1
            jobs.append((count, personals_pairs, options, self.stdout.write, random.randint(0, 10**10)))

        for job in jobs:
            send_messages(job)

        if options["delete"]:
            # Create the "website" and "API" clients; if we don't, the
            # default values in zerver/decorators.py will not work
            # with the Django test suite.
            get_client("website")
            get_client("API")

            if options["test_suite"]:
                # Create test users; the MIT ones are needed to test
                # the Zephyr mirroring codepaths.
                testsuite_mit_users = [
                    ("Fred Sipb (MIT)", "sipbtest@mit.edu"),
                    ("Athena Consulting Exchange User (MIT)", "starnine@mit.edu"),
                    ("Esp Classroom (MIT)", "espuser@mit.edu"),
                ]
                create_users(mit_realm, testsuite_mit_users)

                testsuite_lear_users = [
                    ("King Lear", "king@lear.org"),
                    ("Cordelia Lear", "cordelia@zulip.com"),
                ]
                create_users(lear_realm, testsuite_lear_users)

            if not options["test_suite"]:
                # Initialize the email gateway bot as an API Super User
                email_gateway_bot = get_system_bot(settings.EMAIL_GATEWAY_BOT)
                email_gateway_bot.is_api_super_user = True
                email_gateway_bot.save()

                # To keep the messages.json fixtures file for the test
                # suite fast, don't add these users and subscriptions
                # when running populate_db for the test suite

                zulip_stream_dict = {
                    "devel": {"description": "For developing", "invite_only": False},
                    "all": {"description": "For everything", "invite_only": False},
                    "announce": {"description": "For announcements", "invite_only": False},
                    "design": {"description": "For design", "invite_only": False},
                    "support": {"description": "For support", "invite_only": False},
                    "social": {"description": "For socializing", "invite_only": False},
                    "test": {"description": "For testing", "invite_only": False},
                    "errors": {"description": "For errors", "invite_only": False},
                    "sales": {"description": "For sales discussion", "invite_only": False}
                }  # type: Dict[Text, Dict[Text, Any]]

                # Calculate the maximum number of digits in any extra stream's
                # number, since a stream with name "Extra Stream 3" could show
                # up after "Extra Stream 29". (Used later to pad numbers with
                # 0s).
                maximum_digits = len(str(options['extra_streams'] - 1))

                for i in range(options['extra_streams']):
                    # Pad the number with 0s based on `maximum_digits`.
                    number_str = str(i).zfill(maximum_digits)

                    extra_stream_name = 'Extra Stream ' + number_str

                    zulip_stream_dict[extra_stream_name] = {
                        "description": "Auto-generated extra stream.",
                        "invite_only": False,
                    }

                bulk_create_streams(zulip_realm, zulip_stream_dict)
                # Now that we've created the notifications stream, configure it properly.
                zulip_realm.notifications_stream = get_stream("announce", zulip_realm)
                zulip_realm.save(update_fields=['notifications_stream'])

                # Add a few default streams
                for default_stream_name in ["design", "devel", "social", "support"]:
                    DefaultStream.objects.create(realm=zulip_realm,
                                                 stream=get_stream(default_stream_name, zulip_realm))

                # Now subscribe everyone to these streams
                subscriptions_to_add = []
                event_time = timezone_now()
                all_subscription_logs = []
                profiles = UserProfile.objects.select_related().filter(realm=zulip_realm)
                for i, stream_name in enumerate(zulip_stream_dict):
                    stream = Stream.objects.get(name=stream_name, realm=zulip_realm)
                    recipient = Recipient.objects.get(type=Recipient.STREAM, type_id=stream.id)
                    for profile in profiles:
                        # Subscribe to some streams.
                        s = Subscription(
                            recipient=recipient,
                            user_profile=profile,
                            color=STREAM_ASSIGNMENT_COLORS[i % len(STREAM_ASSIGNMENT_COLORS)])
                        subscriptions_to_add.append(s)

                        log = RealmAuditLog(realm=profile.realm,
                                            modified_user=profile,
                                            modified_stream=stream,
                                            event_last_message_id=0,
                                            event_type='subscription_created',
                                            event_time=event_time)
                        all_subscription_logs.append(log)
                Subscription.objects.bulk_create(subscriptions_to_add)
                RealmAuditLog.objects.bulk_create(all_subscription_logs)

                # These bots are not needed by the test suite
                internal_zulip_users_nosubs = [
                    ("Zulip Commit Bot", "commit-bot@zulip.com"),
                    ("Zulip Trac Bot", "trac-bot@zulip.com"),
                    ("Zulip Nagios Bot", "nagios-bot@zulip.com"),
                ]
                create_users(zulip_realm, internal_zulip_users_nosubs, bot_type=UserProfile.DEFAULT_BOT)

            zulip_cross_realm_bots = [
                ("Zulip Feedback Bot", "feedback@zulip.com"),
            ]
            create_users(zulip_realm, zulip_cross_realm_bots, bot_type=UserProfile.DEFAULT_BOT)

            # Mark all messages as read
            UserMessage.objects.all().update(flags=UserMessage.flags.read)

            if not options["test_suite"]:
                # Update pointer of each user to point to the last message in their
                # UserMessage rows with sender_id=user_profile_id.
                users = list(UserMessage.objects.filter(
                    message__sender_id=F('user_profile_id')).values(
                    'user_profile_id').annotate(pointer=Max('message_id')))
                for user in users:
                    UserProfile.objects.filter(id=user['user_profile_id']).update(
                        pointer=user['pointer'])

            create_user_groups()
            self.stdout.write("Successfully populated test database.\n")