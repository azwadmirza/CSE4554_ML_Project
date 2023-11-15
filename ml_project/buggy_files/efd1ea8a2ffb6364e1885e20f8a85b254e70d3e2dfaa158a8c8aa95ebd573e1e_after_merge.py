    def is_closed(self, stream_id: int) -> bool:
        """Check if a non-idle stream is closed"""
        stream = self.h2_conn.streams.get(stream_id, None)
        if (
            stream is not None
            and
            stream.state_machine.state is not h2.stream.StreamState.CLOSED
        ):
            return False
        else:
            return True