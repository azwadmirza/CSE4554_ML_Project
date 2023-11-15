def assert_can_release():
    assert not IS_PULL_REQUEST, "Cannot release from pull requests"