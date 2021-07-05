import os
import subprocess
from enum import Enum, auto
from utils.pycolor import pprint
from typing import NamedTuple
from .auth import get_csrf_token, auth
from requests import Session
from . import scrape
from . import langs
import requests
import webbrowser


def read_file(file_path: str) -> str:
    with open(file_path, 'r') as f:
        content = f.read().rstrip()
    return content


class TestResult(Enum):
    OK = auto()
    NG = auto()
    TLE = auto()
    RE = auto()


class TestResponse(NamedTuple):
    result: TestResult
    input_val: str
    expected_val: str
    actual_val: str


def get_test_case_dirs(contest, task_name):
    """
    """
    test_case_root_dir = './atcoder/contests/' + \
        contest + '/' + task_name + '/tests/'

    test_case_dirs = list(
        map(
            lambda x: (x, test_case_root_dir + x),
            sorted(os.listdir(test_case_root_dir))
        ))

    return test_case_dirs


def test_all(contest, task, verbose=False):
    print('contest: ', contest)
    print('task: ', task)
    test_dirs = get_test_case_dirs(contest, task)
    target_script = 'atcoder/contests/' + contest + '/' + task + '/main.py'
    all_res = True
    for test_name, test_dir in test_dirs:
        res = test(test_name, test_dir, target_script, verbose=verbose)
        all_res &= res
    return all_res


def test(test_name, test_dir, test_target_path, verbose=False):
    print('case: {} => '.format(test_name), end='')
    input_path = test_dir + '/in.txt'
    output_path = test_dir + '/out.txt'
    res = run_test(test_target_path, input_path, output_path)
    print_result(res, verbose=verbose)
    return res.result == TestResult.OK


def run_test(test_target_path, input_path, output_path) -> TestResponse:
    """
    """
    input_val = read_file(input_path)
    try:
        with open(input_path, 'r') as f:
            std = subprocess.run(
                ['python', test_target_path],
                stdin=f,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                timeout=2.0,
                shell=False,
                check=True,
            )
    except subprocess.TimeoutExpired:
        res = TestResult.TLE
        actual_output = None
        expected_output = None
    except subprocess.CalledProcessError as e:
        res = TestResult.RE
        actual_output = e.output.decode('utf-8').rstrip()
        expected_output = None
    else:
        actual_output = std.stdout.decode('utf-8').rstrip()
        expected_output = read_file(output_path)
        res = TestResult.OK if actual_output == expected_output else TestResult.NG
    return TestResponse(res, input_val, expected_output, actual_output)


def print_result(res: TestResponse, verbose=False):
    result_color = 'green' if res.result == TestResult.OK else 'red'
    pprint('{}'.format(res.result.name), color=result_color)

    if verbose:
        pprint('[input]', color='cyan')
        print(res.input_val)

        if res.result == TestResult.OK:
            pprint('[output]', color='cyan')
            print(res.actual_val)
            print()

        if res.result == TestResult.NG:
            pprint('[expected]', color='green')
            pprint(res.expected_val, color='green', bold=False)
            pprint('[actual]', color='red')
            pprint(res.actual_val, color='red', bold=False)
            print()

        if res.result == TestResult.RE:
            pprint('[output]', color='red')
            pprint(res.actual_val, color='red', bold=False)
            print()

        if res.result == TestResult.TLE:
            print()


CONTEST_URL = 'https://atcoder.jp/contests/'


@auth
def submit(session_logined: Session, contest, task, lang='p'):
    target_script = 'atcoder/contests/' + contest + '/' + task + '/main.py'
    submit_src = read_file(target_script)
    submit_url = CONTEST_URL + contest + '/submit'

    csrf_token = get_csrf_token(submit_url, session_logined)
    tasks_page = scrape.fetch_contest_tasks_page(contest)
    prob_paths = scrape.extract_prob_paths(tasks_page)
    task_screen_name = scrape.get_task_screen_name(prob_paths, task)

    lang_id = langs.get_lang_id(lang)

    submit_info = {"data.TaskScreenName": task_screen_name,
                    "csrf_token": csrf_token,
                    "data.LanguageId": lang_id,
                    "sourceCode": submit_src}
    try:
        res = session_logined.post(submit_url, submit_info)
        res.raise_for_status()
        with open('./result.html', 'w') as f:
            f.write(res.text)
    except requests.exceptions.HTTPError:
        exit(1)

    if res.status_code == 200:
        print('Submit succeeded!')
        print(res.text)
    else:
        print('Submit failed...')
        exit(1)


def _get_submission_result_url(contest):
    """提出結果ページのurlを返す
    :param contest
    :return 提出結果ページのurl
    """
    return CONTEST_URL + contest + '/submissions/me'


def open_submission_page(contest):
    submit_result_url = _get_submission_result_url(contest)
    webbrowser.open(submit_result_url)
