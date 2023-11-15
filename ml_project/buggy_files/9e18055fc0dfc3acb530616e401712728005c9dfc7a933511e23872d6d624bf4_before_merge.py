    def from_proto(cls, proto: qtypes.QuantumTimeSlot):
        slot_type = qenums.QuantumTimeSlot.TimeSlotType(proto.slot_type)
        if proto.HasField('reservation_config'):
            return cls(
                processor_id=proto.processor_name,
                start_time=datetime.datetime.fromtimestamp(proto.start_time.seconds),
                end_time=datetime.datetime.fromtimestamp(proto.end_time.seconds),
                slot_type=slot_type,
                project_id=proto.reservation_config.project_id,
            )
        if proto.HasField('maintenance_config'):
            return cls(
                processor_id=proto.processor_name,
                start_time=datetime.datetime.fromtimestamp(proto.start_time.seconds),
                end_time=datetime.datetime.fromtimestamp(proto.end_time.seconds),
                slot_type=slot_type,
                maintenance_title=proto.maintenance_config.title,
                maintenance_description=proto.maintenance_config.description,
            )
        return cls(
            processor_id=proto.processor_name,
            start_time=datetime.datetime.fromtimestamp(proto.start_time.seconds),
            end_time=datetime.datetime.fromtimestamp(proto.end_time.seconds),
            slot_type=slot_type,
        )