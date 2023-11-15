    def evaluate(self, x_test, y_test):
        """Return the accuracy score between predict value and `y_test`."""
        if len(x_test.shape) != 0 and len(x_test[0].shape) == 3:
            x_test = resize_image_data(x_test, self.resize_height, self.resize_width)
        y_predict = self.predict(x_test)
        return self.metric().evaluate(y_test, y_predict)