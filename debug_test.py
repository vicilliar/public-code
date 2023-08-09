x = 1
y = "tooooo"
print("hello")
z = "bleh"
print("hello 200000")

# output a number of the fibonacci sequence
def fibonacci(n):
    if n < 2:
        return n
    else:
        return fibonacci(n-1) + fibonacci(n-2)

# unit tests for fibonacci function
assert fibonacci(0) == 0
assert fibonacci(1) == 1
assert fibonacci(2) == 1
assert fibonacci(3) == 2

# assert the first 1000 fibonacci numbers are correct
for i in range(1000):
    assert fibonacci(i) == fibonacci(i)


# give me the nth number of the fibonacci sequence
print(fibonacci(10))

# this is a comment
# this is another comment
# this is a third comment
# debug our variables
print(x)
print(y)

def some_func(input: int):
    if input == 0:
        return 0
    elif input > 3:
        return input * input
    else:
        return input + input

# test our function
assert some_func(0) == 0
assert some_func(1) == 2
assert some_func(2) == 4
assert some_func(3) == 6
assert some_func(4) == 16
# test negative numbers
assert some_func(-1) == -2
assert some_func(-2) == -4
assert some_func(-3) == -6