def get_sat_solver_cls(sat_solver_choice=SatSolverChoice.PYCOSAT):
    solvers = odict([
        (SatSolverChoice.PYCOSAT, PycoSatSolver),
        (SatSolverChoice.PYCRYPTOSAT, CryptoMiniSatSolver),
        (SatSolverChoice.PYSAT, PySatSolver),
    ])
    cls = solvers[sat_solver_choice]
    try:
        cls().run(0)
    except Exception as e:
        log.warning("Could not run SAT solver through interface '%s'.", sat_solver_choice)
        log.debug("SAT interface error due to: %s", e, exc_info=True)
    else:
        log.debug("Using SAT solver interface '%s'.", sat_solver_choice)
        return cls
    for solver_choice, cls in solvers.items():
        try:
            cls().run(0)
        except Exception as e:
            log.debug("Attempted SAT interface '%s' but unavailable due to: %s",
                      sat_solver_choice, e)
        else:
            log.debug("Falling back to SAT solver interface '%s'.", sat_solver_choice)
            return cls
    from ..exceptions import CondaDependencyError
    raise CondaDependencyError("Cannot run solver. No functioning SAT implementations available.")