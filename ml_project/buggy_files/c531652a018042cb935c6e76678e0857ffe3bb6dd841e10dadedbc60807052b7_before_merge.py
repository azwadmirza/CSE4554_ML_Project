def install_jupyter_hook(root=None):
    """Make xonsh available as a Jupyter kernel."""
    if not HAVE_JUPYTER:
        print('Could not install Jupyter kernel spec, please install '
              'Jupyter/IPython.')
        return
    spec = {"argv": [sys.executable, "-m", "xonsh.jupyter_kernel",
                     "-f", "{connection_file}"],
            "display_name": "Xonsh",
            "language": "xonsh",
            "codemirror_mode": "shell",
           }
    with TemporaryDirectory() as d:
        os.chmod(d, 0o755)  # Starts off as 700, not user readable
        if sys.platform == 'win32':
            # Ensure that conda-build detects the hard coded prefix
            spec['argv'][0] = spec['argv'][0].replace(os.sep, os.altsep)
        with open(os.path.join(d, 'kernel.json'), 'w') as f:
            json.dump(spec, f, sort_keys=True)
        if 'CONDA_BUILD' in os.environ:
            root = sys.prefix
            if sys.platform == 'win32':
                root = root.replace(os.sep, os.altsep)
        print('Installing Jupyter kernel spec...')
        KernelSpecManager().install_kernel_spec(
            d, 'xonsh', user=('--user' in sys.argv), replace=True,
            prefix=root)