def _to_timestamp(dt: datetime.datetime):
    return timestamp_pb2.Timestamp(seconds=int(dt.timestamp()))