            def applyier(df, **kwargs):
                result = df.apply(func, **applyier_kwargs)
                return result.set_axis(df.axes[axis ^ 1], axis=0)