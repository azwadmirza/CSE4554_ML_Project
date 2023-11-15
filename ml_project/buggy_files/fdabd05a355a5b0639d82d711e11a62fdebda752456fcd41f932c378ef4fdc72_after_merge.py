    def do_POST(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode()
            LOG.info("Received bootloader's request: {}".format(post_data))
            try:
                dest_path = self.path
                r = requests.post(url=dest_path,
                                  data=post_data,
                                  verify=False,
                                  proxies=infection_monkey.control.ControlClient.proxies)
                self.send_response(r.status_code)
            except requests.exceptions.ConnectionError as e:
                LOG.error("Couldn't forward request to the island: {}".format(e))
                self.send_response(404)
            except Exception as e:
                LOG.error("Failed to forward bootloader request: {}".format(e))
            finally:
                self.end_headers()
                self.wfile.write(r.content)
        except Exception as e:
            LOG.error("Failed receiving bootloader telemetry: {}".format(e))