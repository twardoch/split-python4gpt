# This is file2 in a subdirectory
class MyClass:
    """This is MyClass."""

    def __init__(self, value):
        self.value = value  # type: int

    def get_value(self):
        """Returns the value."""
        # A debug print
        print(f"Value is {self.value}")
        return self.value

    def __repr__(self):
        return f"MyClass(value={self.value})"


instance = MyClass(100)
