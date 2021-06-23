import fire
from . import auth


class Commands:
    @staticmethod
    def hello():
        print('hello!')

    @staticmethod
    def login():
        auth.login()


def main():
    fire.Fire(Commands)


if __name__ == '__main__':
    main()
