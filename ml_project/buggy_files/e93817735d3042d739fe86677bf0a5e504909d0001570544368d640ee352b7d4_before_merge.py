def plot(result_dict_file, show, plot_save_file):
    """
    [sys_analyser] draw result DataFrame
    """
    import pandas as pd
    from .plot import plot_result

    result_dict = pd.read_pickle(result_dict_file)
    plot_result(result_dict, show, plot_save_file)