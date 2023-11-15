    def maybe_color_bp(bp):
        if "color" not in kwds:
            setp(bp["boxes"], color=colors[0], alpha=1)
            setp(bp["whiskers"], color=colors[0], alpha=1)
            setp(bp["medians"], color=colors[2], alpha=1)