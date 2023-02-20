class ConfigError(Exception):
    def __init__(self, msg=""):
        super().__init__(msg)


class TaskError(Exception):
    def __init__(self, msg=""):
        super().__init__(msg)


class NLPError(Exception):
    def __init__(self, msg=""):
        super().__init__(msg)
