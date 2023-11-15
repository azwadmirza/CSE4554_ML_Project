def sympy_config(mpl_backend):
    """Sympy configuration"""
    lines = """
from sympy.interactive import init_session
init_session()
%matplotlib {0}
""".format(mpl_backend)
    return lines