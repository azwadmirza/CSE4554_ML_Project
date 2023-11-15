def get_sat_solver_cls(name=None):
    solvers = odict([
        ('pycosat', PycoSatSolver),
        ('pycryptosat', CryptoMiniSatSolver),
        ('pysat', PySatSolver),
    ])
    if name is not None:
        try:
            cls = solvers[name]
        except KeyError:
            raise ValueError('Unknown SAT solver interface: "{}".'.format(name))
        try:
            cls().run(0)
        except Exception:
            raise RuntimeError('Could not run SAT solver through interface "{}".'.format(name))
        else:
            log.debug('Using SAT solver interface "{}".'.format(name))
            return cls
    for name, cls in solvers.items():
        try:
            cls().run(0)
        except Exception:
            log.warn('Could not run SAT solver through interface "{}".'.format(name))
        else:
            log.debug('Using SAT solver interface "{}".'.format(name))
            return cls
    raise RuntimeError('Could not run any SAT solver.')