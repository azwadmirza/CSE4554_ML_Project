    def on_report_sent(self, response):
        if not response:
            return
        sent = response[u'sent']

        success_text = "Successfully sent the report! Thanks for your contribution."
        error_text = "Could not send the report! Please post this issue on GitHub."

        box = QMessageBox(self.window())
        box.setWindowTitle("Report Sent" if sent else "ERROR: Report Sending Failed")
        box.setText(success_text if sent else error_text)
        box.setStyleSheet("QPushButton { color: white; }")
        box.exec_()

        QApplication.quit()