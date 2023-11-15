    def play_mv_by_mvid(cls, mvid):
        mv_model = ControllerApi.api.get_mv_detail(mvid)
        if not ControllerApi.api.is_response_ok(mv_model):
            return

        url_high = mv_model['url_high']
        clipboard = QApplication.clipboard()
        clipboard.setText(url_high)

        if platform.system() == "Linux":
            ControllerApi.player.pause()
            ControllerApi.notify_widget.show_message("通知", "正在尝试调用VLC视频播放器播放MV")
            subprocess.Popen(['vlc', url_high, '--play-and-exit', '-f'])
        elif platform.system().lower() == 'Darwin'.lower():
            ControllerApi.player.pause()
            cls.view.ui.STATUS_BAR.showMessage(u"准备调用 QuickTime Player 播放mv", 4000)
            subprocess.Popen(['open', '-a', 'QuickTime Player', url_high])
        else:
            cls.view.ui.STATUS_BAR.showMessage(u"程序已经将视频的播放地址复制到剪切板", 5000)