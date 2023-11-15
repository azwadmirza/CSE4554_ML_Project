def entry(*a):
    """
    Set a breakpoint at the first instruction executed in
    the target binary.
    """
    global break_on_first_instruction
    break_on_first_instruction = True
    run = 'run ' + ' '.join(map(shlex.quote, a))
    gdb.execute(run, from_tty=False)