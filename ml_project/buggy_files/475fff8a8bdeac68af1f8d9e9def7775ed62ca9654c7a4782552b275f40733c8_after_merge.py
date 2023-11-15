def _known_pattern(name: str, config: Config) -> Optional[Tuple[str, str]]:
    parts = name.split(".")
    module_names_to_check = (".".join(parts[:first_k]) for first_k in range(len(parts), 0, -1))
    for module_name_to_check in module_names_to_check:
        for pattern, placement in config.known_patterns:
            if placement in config.sections and pattern.match(module_name_to_check):
                return (placement, f"Matched configured known pattern {pattern}")

    return None