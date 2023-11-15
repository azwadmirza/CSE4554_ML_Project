def accuracy(
        pred: torch.Tensor,
        target: torch.Tensor,
        num_classes: Optional[int] = None,
        class_reduction: str = 'micro'
) -> torch.Tensor:
    """
    Computes the accuracy classification score

    Args:
        pred: predicted labels
        target: ground truth labels
        num_classes: number of classes
        class_reduction: method to reduce metric score over labels

            - ``'micro'``: calculate metrics globally (default)
            - ``'macro'``: calculate metrics for each label, and find their unweighted mean.
            - ``'weighted'``: calculate metrics for each label, and find their weighted mean.
            - ``'none'``: returns calculated metric per class

    Return:
         A Tensor with the accuracy score.

    Example:

        >>> x = torch.tensor([0, 1, 2, 3])
        >>> y = torch.tensor([0, 1, 2, 2])
        >>> accuracy(x, y)
        tensor(0.7500)

    """
    tps, fps, tns, fns, sups = stat_scores_multiple_classes(
        pred=pred, target=target, num_classes=num_classes)

    return class_reduce(tps, sups, sups, class_reduction=class_reduction)