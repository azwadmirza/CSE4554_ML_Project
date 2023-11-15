    def y_axis_setup():
        items = [0] * len(x_axis)

        for app, tasks in apps_dict.items():
            if option == 'avg':
                task = df_resources[df_resources['task_id'] ==
                                    app][type].astype('float').mean()
            elif option == 'max':
                task = max(
                    df_resources[df_resources['task_id'] == app][type].astype('float'))

            for i in range(len(x_axis) - 1):
                a = task >= x_axis[i]
                b = task < x_axis[i + 1]
                if a and b:
                    items[i] += 1
            if task >= x_axis[-1]:
                items[-1] += 1
        return items