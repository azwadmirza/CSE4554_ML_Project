def get_install_requires():
    requires = ['psutil>=5.3.0']
    if sys.platform.startswith('win'):
        requires.append('bottle')

    return requires