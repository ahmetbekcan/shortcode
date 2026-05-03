

class Animal:
    def __init__(self, name: str):
        self.name = name

    def speak(self) -> str:
        return ""


class Dog(Animal):
    def speak(self) -> str:
        return "Woof"

    def fetch(self, item: str) -> bool:
        return True


def greet(name: str) -> str:
    return f"Hello, {name}"


def add(a: int, b: int) -> int:
    return a + b
