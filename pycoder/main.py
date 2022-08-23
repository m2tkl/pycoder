import fire
from . import auth
from . import code
from . import judge


class Commands:
    @staticmethod
    def login():
        """Login.
        """
        auth.login()

    @staticmethod
    def logout():
        """Logout.
        """
        auth.logout()

    @staticmethod
    def contest(contest):
        """Prepare contest.
        :param contest: Coontest name
        """
        code.prepare_contest(contest)

    @staticmethod
    def test(contest, task, name=None, verbose=False):
        """Run test.
        :param contest: Contest name
        :param task: Target problem (a, b, c, ...)
        :param name: Test case name
        :param verbose: If verbose is True, show full information of test.
        """
        res = judge.test_all(contest, task, name=name, verbose=verbose)

    @staticmethod
    def submit(contest, task, lang='p', force=False):
        """Submit code.
        :param contest: Contest name
        :param task: Target problem (a, b, c, ...)
        :param lang: Submission language
        :param force: Submit forcibly if all test cases are not passed.
        """
        is_all_test_cases_passed = judge.test_all(contest, task)
        if (not is_all_test_cases_passed) and (not force):
            return
        judge.submit(contest, task, lang=lang)
        judge.open_submission_page(contest)

    @staticmethod
    def init():
        """Initialize directory for atcoder
        """
        code.init()


def main():
    fire.Fire(Commands)


if __name__ == '__main__':
    main()
