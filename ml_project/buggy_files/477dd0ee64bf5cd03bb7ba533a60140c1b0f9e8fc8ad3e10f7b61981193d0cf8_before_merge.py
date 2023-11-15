def print_prf_per_type(
    msg: Printer, scores: Dict[str, Dict[str, float]], name: str, type: str
) -> None:
    data = [
        (k, f"{v['p']*100:.2f}", f"{v['r']*100:.2f}", f"{v['f']*100:.2f}")
        for k, v in scores.items()
    ]
    msg.table(
        data,
        header=("", "P", "R", "F"),
        aligns=("l", "r", "r", "r"),
        title=f"{name} (per {type})",
    )