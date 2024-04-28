class CycleException(Exception):
    """Raised when setting a model parent would cause a cycle.

    While representable, cycles can cause infinite loops in many of the
    HierarchicalModel methods.

    Attributes:
        parent: The instance which would have been the parent.
        child: The instance whose parent would have been updated.
    """

    def __init__(self, parent, child, *args):
        super().__init__(*args)
        self.parent = parent
        self.child = child

    def __str__(self):
        return f"Making {self.child} a child of {self.parent} would create a cycle"
