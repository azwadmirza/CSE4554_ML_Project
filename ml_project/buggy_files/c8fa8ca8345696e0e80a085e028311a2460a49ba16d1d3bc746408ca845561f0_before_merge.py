    def y_axis_setup():
        items = []

        for app, tasks in apps_dict.items():
            tmp = []
            if option == 'avg':
                task = df_resources[df_resources['task_id'] ==
                                    app][type].astype('float').mean()
            elif option == 'max':
                task = max(
                    df_resources[df_resources['task_id'] == app][type].astype('float'))

            for i in range(len(x_axis) - 1):
                a = task >= x_axis[i]
                b = task < x_axis[i + 1]
                tmp.append(a & b)
            items = np.sum([items, tmp], axis=0)
        return items