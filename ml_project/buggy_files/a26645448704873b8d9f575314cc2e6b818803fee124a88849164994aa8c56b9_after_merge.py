def configuration(parent_package='',top_path=None):
    from numpy.distutils.misc_util import Configuration
    config = Configuration('special', parent_package, top_path)

    define_macros = []
    if sys.platform=='win32':
#        define_macros.append(('NOINFINITIES',None))
#        define_macros.append(('NONANS',None))
        define_macros.append(('_USE_MATH_DEFINES',None))

    # C libraries
    config.add_library('sc_c_misc',sources=[join('c_misc','*.c')],
                       include_dirs=[get_python_inc(), get_numpy_include_dirs()],
                       macros=define_macros)
    config.add_library('sc_cephes',sources=[join('cephes','*.c')],
                       include_dirs=[get_python_inc(), get_numpy_include_dirs()],
                       macros=define_macros)

    # Fortran/C++ libraries
    config.add_library('sc_mach',sources=[join('mach','*.f')],
                       config_fc={'noopt':(__file__,1)})
    config.add_library('sc_amos',sources=[join('amos','*.f')])
    config.add_library('sc_cdf',sources=[join('cdflib','*.f')])
    config.add_library('sc_specfun',sources=[join('specfun','*.f')])

    # Extension specfun
    config.add_extension('specfun',
                         sources=['specfun.pyf'],
                         f2py_options=['--no-wrap-functions'],
                         define_macros=[],
                         libraries=['sc_specfun'])

    # Extension _ufuncs
    curdir = os.path.abspath(os.path.dirname(__file__))
    config.add_extension('_ufuncs',
                         libraries=['sc_amos','sc_c_misc','sc_cephes','sc_mach',
                                    'sc_cdf', 'sc_specfun'],
                         depends=["_logit.h", "cephes.h",
                                  "amos_wrappers.h",
                                  "cdf_wrappers.h", "specfun_wrappers.h",
                                  "c_misc/misc.h", "cephes/mconf.h", "cephes/cephes_names.h"],
                         sources=['_ufuncs.c', '_logit.c.src',
                                  "amos_wrappers.c", "cdf_wrappers.c", "specfun_wrappers.c"],
                         include_dirs=[curdir],
                         define_macros = define_macros,
                         extra_info=get_info("npymath"))

    # Extension _ufuncs_cxx
    curdir = os.path.abspath(os.path.dirname(__file__))
    config.add_extension('_ufuncs_cxx',
                         sources=['_ufuncs_cxx.cxx',
                                  '_faddeeva.cxx',
                                  'faddeeva_w.cxx',
                                  ],
                         libraries=['sc_cephes'],
                         include_dirs=[curdir],
                         define_macros=define_macros,
                         extra_info=get_info("npymath"))

    config.add_data_files('tests/*.py')
    config.add_data_files('tests/data/README')
    config.add_data_files('tests/data/*.npz')

    return config