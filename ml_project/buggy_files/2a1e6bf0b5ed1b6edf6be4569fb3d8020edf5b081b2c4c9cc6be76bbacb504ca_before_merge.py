def encode(var):
    return maybe_encode_timedelta(maybe_encode_datetime(var.variable))