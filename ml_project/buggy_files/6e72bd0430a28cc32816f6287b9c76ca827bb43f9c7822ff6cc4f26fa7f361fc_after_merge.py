    def maybe_color_bp(bp):
        setp(bp["boxes"], color=colors[0], alpha=1)
        setp(bp["whiskers"], color=colors[1], alpha=1)
        setp(bp["medians"], color=colors[2], alpha=1)
        setp(bp["caps"], color=colors[3], alpha=1)