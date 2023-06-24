class Foo:
    v1 = 123

    def func(self):
        pass

    class Meta:
        v2 = 999
        v3 = 123


print(Foo.v1)
print(Foo.func)
print(Foo.Meta)
print(Foo.Meta.v2)
