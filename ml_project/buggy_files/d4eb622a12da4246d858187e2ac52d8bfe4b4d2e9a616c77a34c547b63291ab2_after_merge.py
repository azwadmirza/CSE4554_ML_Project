def calibration_plot(
        fraction_positives,
        mean_predicted_values,
        algorithm_names=None,
        filename=None
):
    assert len(fraction_positives) == len(mean_predicted_values)

    sns.set_style('whitegrid')

    colors = plt.get_cmap('tab10').colors

    num_algorithms = len(fraction_positives)

    plt.figure(figsize=(9, 9))
    plt.grid(which='both')
    plt.grid(which='minor', alpha=0.5)
    plt.grid(which='major', alpha=0.75)

    plt.plot([0, 1], [0, 1], 'k:', label='Perfectly calibrated')

    for i in range(num_algorithms):
        # ax1.plot(mean_predicted_values[i], fraction_positives[i],
        #         label=algorithms[i] if algorithm_names is not None and i < len(algorithms) else '')

        # sns.tsplot(mean_predicted_values[i], fraction_positives[i], ax=ax1, color=colors[i])

        assert len(mean_predicted_values[i]) == len(fraction_positives[i])
        order = min(3, len(mean_predicted_values[i]) - 1)

        sns.regplot(mean_predicted_values[i], fraction_positives[i],
                    order=order, x_estimator=np.mean, color=colors[i],
                    marker='o', scatter_kws={'s': 40},
                    label=algorithm_names[
                        i] if algorithm_names is not None and i < len(
                        algorithm_names) else '')


    ticks = np.linspace(0.0, 1.0, num=11)
    plt.xlim([-0.05, 1.05])
    plt.xticks(ticks)
    plt.xlabel('Predicted probability')
    plt.ylabel('Observed probability')
    plt.ylim([-0.05, 1.05])
    plt.yticks(ticks)
    plt.legend(loc='lower right')
    plt.title('Calibration (reliability curve)')

    plt.tight_layout()
    ludwig.contrib.contrib_command("visualize_figure", plt.gcf())
    if filename:
        plt.savefig(filename)
    else:
        plt.show()