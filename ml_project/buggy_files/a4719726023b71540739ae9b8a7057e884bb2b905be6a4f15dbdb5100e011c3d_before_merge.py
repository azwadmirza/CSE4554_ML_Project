    def __get_validators__(cls) -> 'CallableGenerator':
        yield list_validator
        yield cls.list_length_validator