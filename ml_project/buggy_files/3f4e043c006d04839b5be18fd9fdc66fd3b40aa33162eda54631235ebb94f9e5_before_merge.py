def upload_distribution():
    """Upload the built package to crates.io."""
    tools.assert_can_release()

    # Yes, cargo really will only look in this file. Yes this is terrible.
    # This only runs on Travis, so we may be assumed to own it, but still.
    unlink_if_present(CARGO_CREDENTIALS)

    # symlink so that the actual secret credentials can't be leaked via the
    # cache.
    os.symlink(tools.CARGO_API_KEY, CARGO_CREDENTIALS)

    # Give the key the right permissions.
    os.chmod(CARGO_CREDENTIALS, int("0600", 8))

    cargo("publish")