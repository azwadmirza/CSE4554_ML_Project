def _has_len(dataloader: DataLoader) -> bool:
    try:
        # try getting the length
        _ = len(dataloader)
        return True
    except TypeError:
        return False