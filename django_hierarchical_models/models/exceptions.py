class CycleException(Exception):
    def __init__(self, parent, child, *args):
        super().__init__(*args)
        self.parent = parent
        self.child = child

    def __str__(self):
        return f"Making {self.child} a child of {self.parent} would create a cycle"
