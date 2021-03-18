
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
            f"Expected: {GREEN}{str(self.expected)}{RESET}\n"
            f"Received: {RED}{str(self.received)}{RESET}"
        )

class TestCase():
    description = None
    bail_on_fail = False

    def __init__(self):
        pass

    def assert_equal(self, expected, received):
        exception = DataMismatch(expected, received)
        try:
            if expected != received:
                raise exception

        except DataMismatch as exception:
            class_name = type(self).__name__
            descriptor = f"{self.description}" if self.description else ""

            print((
                f"\nDataMismatch at {class_name}: {descriptor}\n"
                f"{str(exception)}\n"
            ))

            if self.bail_on_fail:
                exit(1)
        
    def run(self):
        pass


def test():
    a = { "name": "john" }
    b = { "name": "james" }

    class CustomTest(TestCase):
        description = "Two people should be the same"
        bail_on_fail = True

        def __init__(self):
            pass

        def run(self):
            self.assert_equal(a, b)

    ct = CustomTest()
    ct.run()

    ct = CustomTest()
    ct.run()

test()