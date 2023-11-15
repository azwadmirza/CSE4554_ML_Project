def main(staging=False):
    app = journalist_app.create_app(config)
    with app.app_context():
        # Add two test users
        test_password = "correct horse battery staple profanity oil chewy"
        test_otp_secret = "JHCOGO7VCER3EJ4L"

        add_test_user("journalist",
                      test_password,
                      test_otp_secret,
                      is_admin=True)

        if staging:
            return

        add_test_user("dellsberg",
                      test_password,
                      test_otp_secret,
                      is_admin=False)

        journalist_tobe_deleted = add_test_user("clarkkent",
                                                test_password,
                                                test_otp_secret,
                                                is_admin=False,
                                                first_name="Clark",
                                                last_name="Kent")

        # Add test sources and submissions
        num_sources = int(os.getenv('NUM_SOURCES', 2))
        for i in range(num_sources):
            if i == 0:
                # For the first source, the journalist who replied will be deleted
                create_source_and_submissions(journalist_who_replied=journalist_tobe_deleted)
                continue
            create_source_and_submissions()
        # Now let us delete one journalist
        db.session.delete(journalist_tobe_deleted)
        db.session.commit()