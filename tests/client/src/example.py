
class DataMismatch(Exception):
    def __init__(self, expected, received):
        self.expected = expected
        self.received = received
    
    def __str__(self):
        # ANSI Escape Codes
        # https://www.codegrepper.com/code-examples/actionscript/ansi+reset+color+code
        GREEN = "\033[32m"
        RED = "\033[31m"
        RESET = "\033[0m"
        
        return (
            "\n"
            f"Expected: {GREEN}{str(self.expected)}{RESET}\n"
            f"Received: {RED}{str(self.received)}{RESET}\n"
        )


def test():
    a = { "name": "john" }
    b = { "name": "james" }

    raise DataMismatch(1, 2)

test()