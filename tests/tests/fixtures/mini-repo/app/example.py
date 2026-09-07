"""Example module."""

CONSTANT = 7


def alpha(value):
    return value + CONSTANT


def beta(value):
    return value * 2


class Worker:
    """Does small jobs."""

    def run(self):
        return alpha(1)

    def stop(self):
        return None
