def plot_state_qsphere(state, figsize=None, ax=None, show_state_labels=True,
                       show_state_phases=False, use_degrees=False, *, rho=None):
    """Plot the qsphere representation of a quantum state.
    Here, the size of the points is proportional to the probability
    of the corresponding term in the state and the color represents
    the phase.

    Args:
        state (Statevector or DensityMatrix or ndarray): an N-qubit quantum state.
        figsize (tuple): Figure size in inches.
        ax (matplotlib.axes.Axes): An optional Axes object to be used for
            the visualization output. If none is specified a new matplotlib
            Figure will be created and used. Additionally, if specified there
            will be no returned Figure since it is redundant.
        show_state_labels (bool): An optional boolean indicating whether to
            show labels for each basis state.
        show_state_phases (bool): An optional boolean indicating whether to
            show the phase for each basis state.
        use_degrees (bool): An optional boolean indicating whether to use
            radians or degrees for the phase values in the plot.

    Returns:
        Figure: A matplotlib figure instance if the ``ax`` kwag is not set

    Raises:
        ImportError: Requires matplotlib.
        VisualizationError: if input is not a valid N-qubit state.

        QiskitError: Input statevector does not have valid dimensions.

    Example:
        .. jupyter-execute::

           from qiskit import QuantumCircuit
           from qiskit.quantum_info import Statevector
           from qiskit.visualization import plot_state_qsphere
           %matplotlib inline

           qc = QuantumCircuit(2)
           qc.h(0)
           qc.cx(0, 1)

           state = Statevector.from_instruction(qc)
           plot_state_qsphere(state)
    """
    if not HAS_MATPLOTLIB:
        raise ImportError('Must have Matplotlib installed. To install, run "pip install '
                          'matplotlib".')
    try:
        import seaborn as sns
    except ImportError:
        raise ImportError('Must have seaborn installed to use '
                          'plot_state_qsphere. To install, run "pip install seaborn".')
    rho = DensityMatrix(state)
    num = rho.num_qubits
    if num is None:
        raise VisualizationError("Input is not a multi-qubit quantum state.")
    # get the eigenvectors and eigenvalues
    eigvals, eigvecs = linalg.eigh(rho.data)

    if figsize is None:
        figsize = (7, 7)

    if ax is None:
        return_fig = True
        fig = plt.figure(figsize=figsize)
    else:
        return_fig = False
        fig = ax.get_figure()

    gs = gridspec.GridSpec(nrows=3, ncols=3)

    ax = fig.add_subplot(gs[0:3, 0:3], projection='3d')
    ax.axes.set_xlim3d(-1.0, 1.0)
    ax.axes.set_ylim3d(-1.0, 1.0)
    ax.axes.set_zlim3d(-1.0, 1.0)
    ax.axes.grid(False)
    ax.view_init(elev=5, azim=275)

    # start the plotting
    # Plot semi-transparent sphere
    u = np.linspace(0, 2 * np.pi, 25)
    v = np.linspace(0, np.pi, 25)
    x = np.outer(np.cos(u), np.sin(v))
    y = np.outer(np.sin(u), np.sin(v))
    z = np.outer(np.ones(np.size(u)), np.cos(v))
    ax.plot_surface(x, y, z, rstride=1, cstride=1, color='k',
                    alpha=0.05, linewidth=0)

    # Get rid of the panes
    ax.w_xaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
    ax.w_yaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
    ax.w_zaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))

    # Get rid of the spines
    ax.w_xaxis.line.set_color((1.0, 1.0, 1.0, 0.0))
    ax.w_yaxis.line.set_color((1.0, 1.0, 1.0, 0.0))
    ax.w_zaxis.line.set_color((1.0, 1.0, 1.0, 0.0))

    # Get rid of the ticks
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_zticks([])

    # traversing the eigvals/vecs backward as sorted low->high
    for idx in range(eigvals.shape[0]-1, -1, -1):
        if eigvals[idx] > 0.001:
            # get the max eigenvalue
            state = eigvecs[:, idx]
            loc = np.absolute(state).argmax()
            # remove the global phase from max element
            angles = (np.angle(state[loc]) + 2 * np.pi) % (2 * np.pi)
            angleset = np.exp(-1j * angles)
            state = angleset * state

            d = num
            for i in range(2 ** num):
                # get x,y,z points
                element = bin(i)[2:].zfill(num)
                weight = element.count("1")
                zvalue = -2 * weight / d + 1
                number_of_divisions = n_choose_k(d, weight)
                weight_order = bit_string_index(element)
                angle = (float(weight) / d) * (np.pi * 2) + \
                        (weight_order * 2 * (np.pi / number_of_divisions))

                if (weight > d / 2) or ((weight == d / 2) and
                                        (weight_order >= number_of_divisions / 2)):
                    angle = np.pi - angle - (2 * np.pi / number_of_divisions)

                xvalue = np.sqrt(1 - zvalue ** 2) * np.cos(angle)
                yvalue = np.sqrt(1 - zvalue ** 2) * np.sin(angle)

                # get prob and angle - prob will be shade and angle color
                prob = np.real(np.dot(state[i], state[i].conj()))
                colorstate = phase_to_rgb(state[i])

                alfa = 1
                if yvalue >= 0.1:
                    alfa = 1.0 - yvalue

                if prob > 0 and show_state_labels:
                    rprime = 1.3
                    angle_theta = np.arctan2(np.sqrt(1 - zvalue ** 2), zvalue)
                    xvalue_text = rprime * np.sin(angle_theta) * np.cos(angle)
                    yvalue_text = rprime * np.sin(angle_theta) * np.sin(angle)
                    zvalue_text = rprime * np.cos(angle_theta)
                    element_text = '$\\vert' + element + '\\rangle$'
                    if show_state_phases:
                        element_angle = (np.angle(state[i]) + (np.pi * 4)) % (np.pi * 2)
                        if use_degrees:
                            element_text += '\n$%.1f^\\circ$' % (element_angle * 180/np.pi)
                        else:
                            element_angle = pi_check(element_angle, ndigits=3).replace('pi', '\\pi')
                            element_text += '\n$%s$' % (element_angle)
                    ax.text(xvalue_text, yvalue_text, zvalue_text, element_text,
                            ha='center', va='center', size=12)

                ax.plot([xvalue], [yvalue], [zvalue],
                        markerfacecolor=colorstate,
                        markeredgecolor=colorstate,
                        marker='o', markersize=np.sqrt(prob) * 30, alpha=alfa)

                a = Arrow3D([0, xvalue], [0, yvalue], [0, zvalue],
                            mutation_scale=20, alpha=prob, arrowstyle="-",
                            color=colorstate, lw=2)
                ax.add_artist(a)

            # add weight lines
            for weight in range(d + 1):
                theta = np.linspace(-2 * np.pi, 2 * np.pi, 100)
                z = -2 * weight / d + 1
                r = np.sqrt(1 - z ** 2)
                x = r * np.cos(theta)
                y = r * np.sin(theta)
                ax.plot(x, y, z, color=(.5, .5, .5), lw=1, ls=':', alpha=.5)

            # add center point
            ax.plot([0], [0], [0], markerfacecolor=(.5, .5, .5),
                    markeredgecolor=(.5, .5, .5), marker='o', markersize=3,
                    alpha=1)
        else:
            break

    n = 64
    theta = np.ones(n)

    ax2 = fig.add_subplot(gs[2:, 2:])
    ax2.pie(theta, colors=sns.color_palette("hls", n), radius=0.75)
    ax2.add_artist(Circle((0, 0), 0.5, color='white', zorder=1))
    offset = 0.95  # since radius of sphere is one.

    if use_degrees:
        labels = ['Phase\n(Deg)', '0', '90', '180   ', '270']
    else:
        labels = ['Phase', '$0$', '$\\pi/2$', '$\\pi$', '$3\\pi/2$']

    ax2.text(0, 0, labels[0], horizontalalignment='center',
             verticalalignment='center', fontsize=14)
    ax2.text(offset, 0, labels[1], horizontalalignment='center',
             verticalalignment='center', fontsize=14)
    ax2.text(0, offset, labels[2], horizontalalignment='center',
             verticalalignment='center', fontsize=14)
    ax2.text(-offset, 0, labels[3], horizontalalignment='center',
             verticalalignment='center', fontsize=14)
    ax2.text(0, -offset, labels[4], horizontalalignment='center',
             verticalalignment='center', fontsize=14)

    if return_fig:
        if get_backend() in ['module://ipykernel.pylab.backend_inline',
                             'nbAgg']:
            plt.close(fig)
        return fig