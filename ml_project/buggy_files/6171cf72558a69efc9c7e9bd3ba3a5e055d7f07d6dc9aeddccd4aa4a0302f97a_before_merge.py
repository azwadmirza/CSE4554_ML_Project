def _get_log_energy(strided_input: Tensor,
                    epsilon: Tensor,
                    energy_floor: float) -> Tensor:
    r"""Returns the log energy of size (m) for a strided_input (m,*)
    """
    log_energy = torch.max(strided_input.pow(2).sum(1), epsilon).log()  # size (m)
    if energy_floor == 0.0:
        return log_energy
    else:
        return torch.max(log_energy,
                         torch.tensor(math.log(energy_floor)))