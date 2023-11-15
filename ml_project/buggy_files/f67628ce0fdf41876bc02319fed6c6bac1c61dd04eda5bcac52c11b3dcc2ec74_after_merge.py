            def check_quote(token):
                if ";" in str(token):
                    token = "{%s}" % token.replace("}", "}}")
                return token