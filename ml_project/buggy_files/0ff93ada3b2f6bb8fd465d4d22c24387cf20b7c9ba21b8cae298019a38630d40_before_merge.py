    def deserialize(cls, info: TypeInfo, data: JsonDict) -> 'DataclassAttribute':
        return cls(**data)