    def batch_to(data):
        # try to move torchtext data first
        if TORCHTEXT_AVAILABLE and isinstance(data, Batch):

            # Shallow copy because each Batch has a reference to Dataset which contains all examples
            device_data = copy(data)
            for field in data.fields:
                device_field = move_data_to_device(getattr(data, field), device)
                setattr(device_data, field, device_field)
            return device_data

        return data.to(device, non_blocking=True)