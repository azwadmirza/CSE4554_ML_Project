def get_install_requires():
    requires = ['psutil>=2.0.0']
    if sys.platform.startswith('win'):
        requires.append('bottle')

    return requires