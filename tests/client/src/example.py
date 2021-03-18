import time

# ANSI Escape Codes
# https://www.codegrepper.com/code-examples/actionscript/ansi+reset+color+code
GREEN = "\033[32m"
RED = "\033[31m"
YELLOW = "\033[33m"
RESET = "\033[0m"

class DataMismatch(Exception):
    def __init__(self, expected, received):
        self.expected = expected
        self.received = received
    
    def __str__(self):
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
    start_time = None
    tests = []
    counts = { 'passed': 0, 'failed': 0 }

    def add(self, test_case):
        self.tests.append(test_case)

    def run(self):
        # Starting the test timer
        self.start_time = time.time()

        for test in self.tests:
            test_instance = test()
            test_instance.run()

            # Fail
            if test_instance.did_fail:
                self.counts['failed'] += 1
                if self.bail_on_fail or test_instance.bail_on_fail:
                    exit(1)
            # Pass
            else:
                self.counts['passed'] += 1


    def __del__(self):
        '''When instances of the class are garbage collected, printing a message
        describing the results of the tests'''
        seconds_elapsed = time.time() - self.start_time
        milliseconds_elapsed = seconds_elapsed * 1000
        print((
            f"Completed {self.counts['passed'] + self.counts['failed']} tests "
            f"in {milliseconds_elapsed} ms\n"
            f"Passed {GREEN}{self.counts['passed']}{RESET}\n"
            f"Failed {RED}{self.counts['failed']}{RESET}"
        ))


def test():
    class PersonTest(TestCase):
        description = "Two people should be the same"

        def run(self):
            a = { "name": "john" }
            b = { "name": "john" }
            self.assert_equal(a, b)


    class NumberTest(TestCase):
        description = "Two numbers should be the same"
        bail_on_fail = True

        def run(self):
            a = 5
            b = 5
            self.assert_equal(a, b)

    runner = TestRunner()
    runner.add(PersonTest)
    runner.add(NumberTest)
    runner.run()

test()