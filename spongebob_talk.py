from numpy import random


def sPongEbOb_mImiC(text):
    return "".join(x if random.randint(2) else x.upper() for x in text)


if __name__ == '__main__':
    text = "Look at me! I'm mocking you!"
    print(sPongEbOb_mImiC(text))
