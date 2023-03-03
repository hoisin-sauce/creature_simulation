import math


class Vector2:
    def __init__(self, *args):
        arg_len = len(args)
        match arg_len:
            case 0:
                self.x, self.y = 0, 0
            case 1:
                self.x = args[0]
                self.y = args[0]
            case 2:
                self.x, self.y = args
            case _:
                raise ValueError(f"Too many arguments < 3 were expected {arg_len} were given")

    @property
    def magnitude(self):
        return math.sqrt(self.x**2 + self.y**2)

    def normalised(self):
        if self.magnitude != 0:
            return Vector2(self.x / self.magnitude, self.y / self.magnitude)
        return Vector2()

    def __mul__(self, other):
        if isinstance(other, int):
            return Vector2(self.x * other, self.y * other)
        elif isinstance(other, Vector2):
            return Vector2(self.x * other.x, self.y * other.y)
        else:
            raise TypeError

    def __add__(self, other):
        if isinstance(other, Vector2):
            return Vector2(self.x + other.x, self.y + other.y)
        else:
            raise TypeError

    def __sub__(self, other):
        if isinstance(other, Vector2):
            return Vector2(self.x - other.x, self.y - other.y)
        else:
            raise TypeError

    def __div__(self, other):
        if isinstance(other, [int, float]):
            return Vector2(self.x / other, self.y / other)
        elif isinstance(other, Vector2):
            return Vector2(self.x / other, self.y / other)
        else:
            raise TypeError

    def __repr__(self):
        return f"Vector2 [{self.x}, {self.y}]"


if __name__ == "__main__":
    # test cases
    n = Vector2(3, 4)
    n.normalise()
    n *= 2
    print(n)
