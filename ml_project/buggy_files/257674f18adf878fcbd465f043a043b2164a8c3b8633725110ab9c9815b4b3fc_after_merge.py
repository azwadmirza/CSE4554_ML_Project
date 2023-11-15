def move_data_to_device(batch: Any, device: torch.device):
    """
    Transfers a collection of data to the given device. Any object that defines a method
    ``to(device)`` will be moved and all other objects in the collection will be left untouched.

    Args:
        batch: A tensor or collection of tensors or anything that has a method `.to(...)`.
            See :func:`apply_to_collection` for a list of supported collection types.
        device: The device to which the data should be moved

    Return:
        the same collection but with all contained tensors residing on the new device.

    See Also:
        - :meth:`torch.Tensor.to`
        - :class:`torch.device`
    """

    def batch_to(data):
        # try to move torchtext data first
        if TORCHTEXT_AVAILABLE and isinstance(data, Batch):

            # Shallow copy because each Batch has a reference to Dataset which contains all examples
            device_data = copy(data)
            for field, field_value in data.dataset.fields.items():
                if field_value is None:
                    continue
                device_field = move_data_to_device(getattr(data, field), device)
                setattr(device_data, field, device_field)
            return device_data

        kwargs = dict(non_blocking=True) if isinstance(data, torch.Tensor) else {}
        return data.to(device, **kwargs)

    dtype = (TransferableDataType, Batch) if TORCHTEXT_AVAILABLE else TransferableDataType
    return apply_to_collection(batch, dtype=dtype, function=batch_to)