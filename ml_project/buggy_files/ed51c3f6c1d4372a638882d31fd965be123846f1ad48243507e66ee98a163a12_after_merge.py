def playstate(state):
    """Convert iTunes playstate to API representation."""
    # pylint: disable=too-many-return-statements
    if state is None:
        return const.PLAY_STATE_NO_MEDIA
    elif state == 0:
        return const.PLAY_STATE_IDLE
    elif state == 1:
        return const.PLAY_STATE_LOADING
    elif state == 3:
        return const.PLAY_STATE_PAUSED
    elif state == 4:
        return const.PLAY_STATE_PLAYING
    elif state == 5:
        return const.PLAY_STATE_FAST_FORWARD
    elif state == 6:
        return const.PLAY_STATE_FAST_BACKWARD

    raise exceptions.UnknownPlayState('Unknown playstate: ' + str(state))