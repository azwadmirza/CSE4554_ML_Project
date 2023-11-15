def roll_die(n):
    """
    Roll an n-sided quantum die.
    """
    addresses = list(range(qubits_needed(n)))
    if n not in dice:
        dice[n] = die_program(n)
    die = dice[n]
    # Generate results and do rejection sampling.
    while True:
        results = qvm.run(die, addresses, BATCH_SIZE)
        for r in results:
            x = process_result(r) + 1
            if 0 < x <= n:
                return x