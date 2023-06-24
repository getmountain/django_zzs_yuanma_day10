from decimal import Decimal

v1 = Decimal("100")
v2 = Decimal("140")
v3 = v1 + 100
print(v3, type(v3))

v3 = int(v3)

print(v3, type(v3))
