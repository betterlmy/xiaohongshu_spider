def test1():
    global x
    x = 1

if __name__ == '__main__':
    test1()
    x = 0
    print(x)