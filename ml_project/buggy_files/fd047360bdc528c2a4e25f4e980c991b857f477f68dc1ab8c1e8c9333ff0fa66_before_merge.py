    def get_domain(self, address):
        try:
            dom = re.search(r'(//|^)([a-z0-9.-]*[a-z]\.[a-z][a-z-]*?(?:[/:].*|$))', address).group(2)
            if not self.in_whitelist(dom):
                if get_tld(url_normalize(dom), fail_silently=True):
                    return url_normalize(dom)
            return None
        except AttributeError:
            return None
        except UnicodeError:  # url_normalize's error, happens when something weird matches regex
            self.logger.info("Caught UnicodeError on %r.", address)
            return None