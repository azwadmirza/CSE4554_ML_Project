def torch_multinomial(input, num_samples, replacement=False):
    """
    Like `torch.multinomial()` but works with cuda tensors.
    Does not support keyword argument `out`.
    """
    if input.is_cuda:
        return torch.multinomial(input.cpu(), num_samples, replacement).cuda(input.get_device())
    else:
        return torch.multinomial(input, num_samples, replacement)