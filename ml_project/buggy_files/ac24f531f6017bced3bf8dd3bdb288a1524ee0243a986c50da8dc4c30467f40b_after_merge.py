def plot_gate_map(backend, figsize=None,
                  plot_directed=False,
                  label_qubits=True,
                  qubit_size=24,
                  line_width=4,
                  font_size=12,
                  qubit_color=None,
                  qubit_labels=None,
                  line_color=None,
                  font_color='w',
                  ax=None):
    """Plots the gate map of a device.

    Args:
        backend (BaseBackend): A backend instance,
        figsize (tuple): Output figure size (wxh) in inches.
        plot_directed (bool): Plot directed coupling map.
        label_qubits (bool): Label the qubits.
        qubit_size (float): Size of qubit marker.
        line_width (float): Width of lines.
        font_size (int): Font size of qubit labels.
        qubit_color (list): A list of colors for the qubits
        qubit_labels (list): A list of qubit labels
        line_color (list): A list of colors for each line from coupling_map.
        font_color (str): The font color for the qubit labels.
        ax (Axes): A Matplotlib axes instance.

    Returns:
        Figure: A Matplotlib figure instance.

    Raises:
        QiskitError: if tried to pass a simulator.
        ImportError: if matplotlib not installed.

    Example:
        .. jupyter-execute::
            :hide-code:
            :hide-output:

            from qiskit.test.ibmq_mock import mock_get_backend
            mock_get_backend('FakeVigo')

        .. jupyter-execute::

           from qiskit import QuantumCircuit, execute, IBMQ
           from qiskit.visualization import plot_gate_map
           %matplotlib inline

           provider = IBMQ.load_account()
           accountProvider = IBMQ.get_provider(hub='ibm-q')
           backend = accountProvider.get_backend('ibmq_vigo')
           plot_gate_map(backend)
    """
    if not HAS_MATPLOTLIB:
        raise ImportError('Must have Matplotlib installed. To install, '
                          'run "pip install matplotlib".')

    if backend.configuration().simulator:
        raise QiskitError('Requires a device backend, not simulator.')

    input_axes = False
    if ax:
        input_axes = True

    mpl_data = {}

    mpl_data[1] = [[0, 0]]

    mpl_data[5] = [[1, 0], [0, 1], [1, 1], [1, 2], [2, 1]]

    mpl_data[7] = [[0, 0], [0, 1], [0, 2],
                   [1, 1],
                   [2, 0], [2, 1], [2, 2]]

    mpl_data[20] = [[0, 0], [0, 1], [0, 2], [0, 3], [0, 4],
                    [1, 0], [1, 1], [1, 2], [1, 3], [1, 4],
                    [2, 0], [2, 1], [2, 2], [2, 3], [2, 4],
                    [3, 0], [3, 1], [3, 2], [3, 3], [3, 4]]

    mpl_data[15] = [[0, 0], [0, 1], [0, 2], [0, 3], [0, 4],
                    [0, 5], [0, 6], [1, 7], [1, 6], [1, 5],
                    [1, 4], [1, 3], [1, 2], [1, 1], [1, 0]]

    mpl_data[16] = [[1, 0], [0, 0], [0, 1], [0, 2], [0, 3],
                    [0, 4], [0, 5], [0, 6], [0, 7], [1, 7],
                    [1, 6], [1, 5], [1, 4], [1, 3], [1, 2], [1, 1]]

    mpl_data[27] = [[1, 0], [1, 1], [2, 1], [3, 1], [1, 2],
                    [3, 2], [0, 3], [1, 3], [3, 3], [4, 3],
                    [1, 4], [3, 4], [1, 5], [2, 5], [3, 5],
                    [1, 6], [3, 6], [0, 7], [1, 7], [3, 7],
                    [4, 7], [1, 8], [3, 8], [1, 9], [2, 9],
                    [3, 9], [3, 10]]

    mpl_data[28] = [[0, 2], [0, 3], [0, 4], [0, 5], [0, 6],
                    [1, 2], [1, 6],
                    [2, 0], [2, 1], [2, 2], [2, 3], [2, 4],
                    [2, 5], [2, 6], [2, 7], [2, 8],
                    [3, 0], [3, 4], [3, 8],
                    [4, 0], [4, 1], [4, 2], [4, 3], [4, 4],
                    [4, 5], [4, 6], [4, 7], [4, 8]]

    mpl_data[53] = [[0, 2], [0, 3], [0, 4], [0, 5], [0, 6],
                    [1, 2], [1, 6],
                    [2, 0], [2, 1], [2, 2], [2, 3], [2, 4],
                    [2, 5], [2, 6], [2, 7], [2, 8],
                    [3, 0], [3, 4], [3, 8],
                    [4, 0], [4, 1], [4, 2], [4, 3], [4, 4],
                    [4, 5], [4, 6], [4, 7], [4, 8],
                    [5, 2], [5, 6],
                    [6, 0], [6, 1], [6, 2], [6, 3], [6, 4],
                    [6, 5], [6, 6], [6, 7], [6, 8],
                    [7, 0], [7, 4], [7, 8],
                    [8, 0], [8, 1], [8, 2], [8, 3], [8, 4],
                    [8, 5], [8, 6], [8, 7], [8, 8],
                    [9, 2], [9, 6]]

    mpl_data[65] = [[0, 0], [0, 1], [0, 2], [0, 3], [0, 4],
                    [0, 5], [0, 6], [0, 7], [0, 8], [0, 9],
                    [1, 0], [1, 4], [1, 8],
                    [2, 0], [2, 1], [2, 2], [2, 3], [2, 4],
                    [2, 5], [2, 6], [2, 7], [2, 8], [2, 9], [2, 10],
                    [3, 2], [3, 6], [3, 10],
                    [4, 0], [4, 1], [4, 2], [4, 3], [4, 4],
                    [4, 5], [4, 6], [4, 7], [4, 8], [4, 9], [4, 10],
                    [5, 0], [5, 4], [5, 8],
                    [6, 0], [6, 1], [6, 2], [6, 3], [6, 4],
                    [6, 5], [6, 6], [6, 7], [6, 8], [6, 9], [6, 10],
                    [7, 2], [7, 6], [7, 10],
                    [8, 1], [8, 2], [8, 3], [8, 4],
                    [8, 5], [8, 6], [8, 7], [8, 8], [8, 9], [8, 10]]

    config = backend.configuration()
    num_qubits = config.n_qubits
    cmap = config.coupling_map

    if qubit_labels is None:
        qubit_labels = list(range(num_qubits))
    else:
        if len(qubit_labels) != num_qubits:
            raise QiskitError('Length of qubit labels '
                              'does not equal number '
                              'of qubits.')

    if num_qubits in mpl_data.keys():
        grid_data = mpl_data[num_qubits]
    else:
        if not input_axes:
            fig, ax = plt.subplots(figsize=(5, 5))  # pylint: disable=invalid-name
            ax.axis('off')
            return fig

    x_max = max([d[1] for d in grid_data])
    y_max = max([d[0] for d in grid_data])
    max_dim = max(x_max, y_max)

    if figsize is None:
        if num_qubits == 1 or (x_max / max_dim > 0.33 and y_max / max_dim > 0.33):
            figsize = (5, 5)
        else:
            figsize = (9, 3)

    if ax is None:
        fig, ax = plt.subplots(figsize=figsize)  # pylint: disable=invalid-name
        ax.axis('off')

    # set coloring
    if qubit_color is None:
        qubit_color = ['#648fff'] * config.n_qubits
    if line_color is None:
        line_color = ['#648fff'] * len(cmap) if cmap else []

    # Add lines for couplings
    if num_qubits != 1:
        for ind, edge in enumerate(cmap):
            is_symmetric = False
            if edge[::-1] in cmap:
                is_symmetric = True
            y_start = grid_data[edge[0]][0]
            x_start = grid_data[edge[0]][1]
            y_end = grid_data[edge[1]][0]
            x_end = grid_data[edge[1]][1]

            if is_symmetric:
                if y_start == y_end:
                    x_end = (x_end - x_start) / 2 + x_start

                elif x_start == x_end:
                    y_end = (y_end - y_start) / 2 + y_start

                else:
                    x_end = (x_end - x_start) / 2 + x_start
                    y_end = (y_end - y_start) / 2 + y_start
            ax.add_artist(plt.Line2D([x_start, x_end], [-y_start, -y_end],
                                     color=line_color[ind], linewidth=line_width,
                                     zorder=0))
            if plot_directed:
                dx = x_end - x_start  # pylint: disable=invalid-name
                dy = y_end - y_start  # pylint: disable=invalid-name
                if is_symmetric:
                    x_arrow = x_start + dx * 0.95
                    y_arrow = -y_start - dy * 0.95
                    dx_arrow = dx * 0.01
                    dy_arrow = -dy * 0.01
                    head_width = 0.15
                else:
                    x_arrow = x_start + dx * 0.5
                    y_arrow = -y_start - dy * 0.5
                    dx_arrow = dx * 0.2
                    dy_arrow = -dy * 0.2
                    head_width = 0.2
                ax.add_patch(mpatches.FancyArrow(x_arrow,
                                                 y_arrow,
                                                 dx_arrow,
                                                 dy_arrow,
                                                 head_width=head_width,
                                                 length_includes_head=True,
                                                 edgecolor=None,
                                                 linewidth=0,
                                                 facecolor=line_color[ind],
                                                 zorder=1))

    # Add circles for qubits
    for var, idx in enumerate(grid_data):
        _idx = [idx[1], -idx[0]]
        width = _GraphDist(qubit_size, ax, True)
        height = _GraphDist(qubit_size, ax, False)
        ax.add_artist(mpatches.Ellipse(
            _idx, width, height, color=qubit_color[var], zorder=1))
        if label_qubits:
            ax.text(*_idx, s=qubit_labels[var],
                    horizontalalignment='center',
                    verticalalignment='center',
                    color=font_color, size=font_size, weight='bold')
    ax.set_xlim([-1, x_max + 1])
    ax.set_ylim([-(y_max + 1), 1])
    if not input_axes:
        if get_backend() in ['module://ipykernel.pylab.backend_inline',
                             'nbAgg']:
            plt.close(fig)
        return fig
    return None