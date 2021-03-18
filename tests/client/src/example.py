
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
    did_fail = False

    def __init__(self):
        pass

    def assert_equal(self, expected, received):
        exception = DataMismatch(expected, received)
        try:
            if expected != received:
                raise exception

        except DataMismatch as exception:
            self.did_fail = True
            class_name = type(self).__name__
            descriptor = f"{self.description}" if self.description else ""

            print((
                f"\nDataMismatch at {class_name}: {descriptor}\n"
                f"{str(exception)}\n"
            ))

    def run(self):
        pass

class TestRunner():
    bail_on_fail = False
    tests = []

    def add(self, test_case):
        self.tests.append(test_case)

    def run(self):
        for test in self.tests:
            test_instance = test()
            test_instance.run()

            if test_instance.did_fail:
                if self.bail_on_fail or test_instance.bail_on_fail:
                    exit(1)


def test():
    class PersonTest(TestCase):
        description = "Two people should be the same"

        def run(self):
            a = { "name": "jhn" }
            b = { "name": "john" }
            self.assert_equal(a, b)


    class NumberTest(TestCase):
        description = "Two numbers should be the same"
        bail_on_fail = True

        def run(self):
            a = 4
            b = 5
            self.assert_equal(a, b)

    runner = TestRunner()
    runner.add(NumberTest)
    runner.add(PersonTest)
    runner.run()

test()