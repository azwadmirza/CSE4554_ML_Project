def userlimit(channel):
    if channel.user_limit == 0 or channel.user_limit > len(channel.members) + 1:
        return False
    return True