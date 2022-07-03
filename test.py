class Foo:
    def __init__(self):
        self.a = [1, 2, 3]

    def doForA(self, func):
        for a in range(3):
            func(a)
    
    def func(self):
        def inner(a):
            print(self.a[a])
        self.doForA(inner)

Foo().func()
