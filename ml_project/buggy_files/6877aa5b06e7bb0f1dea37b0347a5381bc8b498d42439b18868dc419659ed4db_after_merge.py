def _to_timestamp(dt: Optional[datetime.datetime]) -> Optional[timestamp_pb2.Timestamp]:
    if dt is not None:
        return timestamp_pb2.Timestamp(seconds=int(dt.timestamp()))
    return None