def get_num_classes(
        pred: torch.Tensor,
        target: torch.Tensor,
        num_classes: Optional[int] = None,
) -> int:
    """
    Calculates the number of classes for a given prediction and target tensor.

        Args:
            pred: predicted values
            target: true labels
            num_classes: number of classes if known

        Return:
            An integer that represents the number of classes.
    """
    num_target_classes = int(target.max().detach().item() + 1)
    num_pred_classes = int(pred.max().detach().item() + 1)
    num_all_classes = max(num_target_classes, num_pred_classes)

    if num_classes is None:
        num_classes = num_all_classes
    elif num_classes != num_all_classes:
        rank_zero_warn(f'You have set {num_classes} number of classes if different from'
                       f' predicted ({num_pred_classes}) and target ({num_target_classes}) number of classes')
    return num_classes