def _has_len(dataloader: DataLoader) -> bool:
    """ Checks if a given Dataloader has __len__ method implemented i.e. if
    it is a finite dataloader or infinite dataloader """
    try:
        # try getting the length
        if len(dataloader) == 0:
            raise ValueError('Dataloader returned 0 length. Please make sure'
                             ' that your Dataloader atleast returns 1 batch')
        return True
    except TypeError:
        return False