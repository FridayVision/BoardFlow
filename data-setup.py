def hello_world():
    print("Hello World!")

def true_block():
    return True


if __name__ == "__main__":
    if not true_block():
        hello_world()
