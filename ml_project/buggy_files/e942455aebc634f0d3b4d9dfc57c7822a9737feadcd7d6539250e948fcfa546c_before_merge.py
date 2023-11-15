def _get_mpi_implementation_flags():
    output = six.StringIO()
    command = 'mpirun --version'
    try:
        exit_code = safe_shell_exec.execute(command, stdout=output,
                                            stderr=output)
        output_msg = output.getvalue()
    except Exception:
        print(traceback.format_exc(), file=sys.stderr)
        return None
    finally:
        output.close()

    if exit_code == 0:
        if 'Open MPI' in output_msg:
            return list(_OMPI_FLAGS)
        elif 'IBM Spectrum MPI' in output_msg:
            return list(_SMPI_FLAGS)
        elif 'MPICH' in output_msg:
            return list(_MPICH_FLAGS)
        print('Open MPI/Spectrum MPI/MPICH not found in output of mpirun --version.',
              file=sys.stderr)
        return None
    else:
        print("Was not able to run %s:\n%s" % (command, output_msg),
              file=sys.stderr)
        return None