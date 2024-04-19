class AlreadyHasParentException(Exception):
    def __init__(self, child, *args):
        super().__init__(*args)
        self.child = child

    def __str__(self):
        return f"{self.child} already has a parent"


class NotAChildException(Exception):
    def __init__(self, parent, child, *args):
        super().__init__(*args)
        self.parent = parent
        self.child = child

    def __str__(self):
        return f"{self.child} is not a child of {self.parent}"


class CycleException(Exception):
    def __init__(self, parent, child, *args):
        super().__init__(*args)
        self.parent = parent
        self.child = child

    def __str__(self):
        return f"Making {self.child} a child of {self.parent} would create a cycle"
