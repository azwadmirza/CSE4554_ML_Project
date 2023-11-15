    def __str__(self) -> str:
        if self == AdexEventType.BOND:
            return 'deposit'
        if self == AdexEventType.UNBOND:
            return 'withdraw'
        if self == AdexEventType.UNBOND_REQUEST:
            return 'withdraw request'
        if self == AdexEventType.CHANNEL_WITHDRAW:
            return 'claim'
        raise AttributeError(f'Corrupt value {self} for EventType -- Should never happen')