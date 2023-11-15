    def __init__(self, *args, **kwargs):
        '''

        Keywords:
            filename (str) : a path to a Jupyter notebook (".ipynb") file

        '''
        nbformat = import_required('nbformat', 'The Bokeh notebook application handler requires Jupyter Notebook to be installed.')
        nbconvert = import_required('nbconvert', 'The Bokeh notebook application handler requires Jupyter Notebook to be installed.')

        if 'filename' not in kwargs:
            raise ValueError('Must pass a filename to NotebookHandler')
        filename = kwargs['filename']

        with open(filename) as f:
            nb = nbformat.read(f, nbformat.NO_CONVERT)
            exporter = nbconvert.PythonExporter()
            source, meta = exporter.from_notebook_node(nb)
            kwargs['source'] = source

        super(NotebookHandler, self).__init__(*args, **kwargs)