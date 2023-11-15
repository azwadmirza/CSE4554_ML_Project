    def batch_to(data):
        # try to move torchtext data first
        if TORCHTEXT_AVAILABLE and isinstance(data, Batch):

            # Shallow copy because each Batch has a reference to Dataset which contains all examples
            device_data = copy(data)
            for field in data.fields:
                # Batch contains output of Field.process(...) which is tensor hence .to(...) exists
                device_field = getattr(data, field).to(device, non_blocking=True)
                setattr(device_data, field, device_field)
            return device_data
        else:
            return data.to(device, non_blocking=True)