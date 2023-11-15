def track_limit(track, maxlength):
    try:
        length = round(track.length / 1000)
    except AttributeError:
        length = round(track / 1000)

    if maxlength < length <= 900000000000000:  # livestreams return 9223372036854775807ms
        return False
    return True