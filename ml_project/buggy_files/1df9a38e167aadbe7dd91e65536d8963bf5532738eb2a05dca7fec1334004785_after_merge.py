def help_solvers():
    import pyomo.environ
    wrapper = textwrap.TextWrapper(replace_whitespace=False)
    print("")
    print("Pyomo Solvers and Solver Managers")
    print("---------------------------------")

    print(wrapper.fill("Pyomo uses 'solver managers' to execute 'solvers' that perform optimization and other forms of model analysis.  A solver directly executes an optimizer, typically using an executable found on the user's PATH environment.  Solver managers support a flexible mechanism for asyncronously executing solvers either locally or remotely.  The following solver managers are available in Pyomo:"))
    print("")
    solvermgr_list = pyomo.opt.SolverManagerFactory.services()
    solvermgr_list = sorted( filter(lambda x: '_' != x[0], solvermgr_list) )
    n = max(map(len, solvermgr_list))
    wrapper = textwrap.TextWrapper(subsequent_indent=' '*(n+9))
    for s in solvermgr_list:
        format = '    %-'+str(n)+'s     %s'
        print(wrapper.fill(format % (s , pyomo.opt.SolverManagerFactory.doc(s))))
    print("")
    wrapper = textwrap.TextWrapper(subsequent_indent='')
    print(wrapper.fill("If no solver manager is specified, Pyomo uses the serial solver manager to execute solvers locally.  The pyro and phpyro solver managers require the installation and configuration of the pyro software.  The neos solver manager is used to execute solvers on the NEOS optimization server."))
    print("")

    print("")
    print("Serial Solver Interfaces")
    print("------------------------")
    print(wrapper.fill("The serial, pyro and phpyro solver managers support the following solver interfaces:"))
    print("")
    solver_list = pyomo.opt.SolverFactory.services()
    solver_list = sorted( filter(lambda x: '_' != x[0], solver_list) )
    n = max(map(len, solver_list))
    wrapper = textwrap.TextWrapper(subsequent_indent=' '*(n+9))
    try:
        # Disable warnings
        logging.disable(logging.WARNING)
        for s in solver_list:
            # Create a solver, and see if it is available
            with pyomo.opt.SolverFactory(s) as opt:
                if s == 'py' or (hasattr(opt, "_metasolver") and opt._metasolver):
                    # py is a metasolver, but since we don't specify a subsolver
                    # for this test, opt is actually an UnknownSolver, so we
                    # can't try to get the _metasolver attribute from it.
                    # Also, default to False if the attribute isn't implemented
                    msg = '    %-'+str(n)+'s   + %s'
                elif opt.available(False):
                    msg = '    %-'+str(n)+'s   * %s'
                else:
                    msg = '    %-'+str(n)+'s     %s'
                print(wrapper.fill(msg % (s, pyomo.opt.SolverFactory.doc(s))))
    finally:
        # Reset logging level
        logging.disable(logging.NOTSET)
    print("")
    wrapper = textwrap.TextWrapper(subsequent_indent='')
    print(wrapper.fill("An asterisk indicates solvers that are currently available to be run from Pyomo with the serial solver manager. A plus indicates meta-solvers, that are always available."))
    print('')
    print(wrapper.fill('Pyomo also supports solver interfaces that are wrappers around third-party solver interfaces. These interfaces require a subsolver specification that indicates the solver being executed.  For example, the following indicates that the ipopt solver will be used:'))
    print('')
    print('   asl:ipopt')
    print('')
    print(wrapper.fill('The asl interface provides a generic wrapper for all solvers that use the AMPL Solver Library.'))
    print('')
    print(wrapper.fill('Note that subsolvers can not be enumerated automatically for these interfaces.  However, if a solver is specified that is not found, Pyomo assumes that the asl solver interface is being used.  Thus the following solver name will launch ipopt if the \'ipopt\' executable is on the user\'s path:'))
    print('')
    print('   ipopt')
    print('')
    try:
        logging.disable(logging.WARNING)
        import pyomo.neos.kestrel
        kestrel = pyomo.neos.kestrel.kestrelAMPL()
        #print "HERE", solver_list
        solver_list = list(set([name[:-5].lower() for name in kestrel.solvers() if name.endswith('AMPL')]))
        #print "HERE", solver_list
        if len(solver_list) > 0:
            print("")
            print("NEOS Solver Interfaces")
            print("----------------------")
            print(wrapper.fill("The neos solver manager supports solver interfaces that can be executed remotely on the NEOS optimization server.  The following solver interfaces are available with your current system configuration:"))
            print("")
            solver_list = sorted(solver_list)
            n = max(map(len, solver_list))
            format = '    %-'+str(n)+'s     %s'
            for name in solver_list:
                print(wrapper.fill(format % (name , pyomo.neos.doc.get(name,'Unexpected NEOS solver'))))
            print("")
        else:
            print("")
            print("NEOS Solver Interfaces")
            print("----------------------")
            print(wrapper.fill("The neos solver manager supports solver interfaces that can be executed remotely on the NEOS optimization server.  This server is not available with your current system configuration."))
            print("")
    except ImportError:
        pass
    finally:
        logging.disable(logging.NOTSET)