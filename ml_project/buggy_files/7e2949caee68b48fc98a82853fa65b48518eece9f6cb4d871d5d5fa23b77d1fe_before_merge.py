def _get_user_info(user=None):
    """
    Wrapper for user.info Salt function
    """
    if not user:
        # Get user Salt runnining as
        user = __salt__["config.option"]("user")

    userinfo = __salt__["user.info"](user)

    if not userinfo:
        if user == "salt":
            # Special case with `salt` user:
            # if it doesn't exist then fall back to user Salt running as
            userinfo = _get_user_info()
        else:
            raise SaltInvocationError("User {0} does not exist".format(user))

    return userinfo