    def on_emptying_tokens(self, data):
        if not data:
            return
        json_data = json.dumps(data)

        if has_qr:
            self.empty_tokens_barcode_dialog = QWidget()
            self.empty_tokens_barcode_dialog.setWindowTitle("Please scan the following QR code")
            self.empty_tokens_barcode_dialog.setGeometry(10, 10, 500, 500)
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_M,
                box_size=10,
                border=5,
            )
            qr.add_data(json_data)
            qr.make(fit=True)

            img = qr.make_image()  # PIL format

            qim = ImageQt(img)
            pixmap = QtGui.QPixmap.fromImage(qim).scaled(600, 600, QtCore.Qt.KeepAspectRatio)
            label = QLabel(self.empty_tokens_barcode_dialog)
            label.setPixmap(pixmap)
            self.empty_tokens_barcode_dialog.resize(pixmap.width(), pixmap.height())
            self.empty_tokens_barcode_dialog.show()
        else:
            ConfirmationDialog.show_error(self.window(), DEPENDENCY_ERROR_TITLE, DEPENDENCY_ERROR_MESSAGE)