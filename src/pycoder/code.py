from typing import Dict
from . import scrape
from .scrape import SampleTestCases
import os
import pathlib

def read_file(filepath: str) -> str:
    """ファイルの中身を返す
    :param filepath ファイルのパス
    :return content ファイルの中身
    """
    with open(filepath, 'r') as f:
        content = f.read().rstrip()
    return content


def fetch_contet_test_cases(contest) -> Dict[str, SampleTestCases]:
    """指定されたコンテストの各問題のサンプルテストケースを取得する。
    :param contest: コンテストの名前 (ex: 'abc123')
    :return 各問題のテストケース
    """
    contest_tasks_page = scrape.fetch_contest_tasks_page(contest)
    prob_paths = scrape.extract_prob_paths(contest_tasks_page)
    prob_urls = scrape.prob_paths_to_urls(prob_paths)

    contest_test_cases = scrape.fetch_sample_test_cases(prob_urls)
    return contest_test_cases


def prepare_contest(contest):
    """contest用のディレクトリを作成し、mainスクリプトファイル、テストケースを用意する。
    ./atcoder/contests/
        - abc123/
            - a/
                - main.py
                - tests/
            - b/
                - main.py
                - tests/
            ...
        - abc456/
            ...
    """
    base_dir = './atcoder/contests/'
    contest_dir = base_dir + contest + '/'

    # make contest directory
    if not os.path.exists(contest_dir):
        os.makedirs(contest_dir)

    contest_test_cases = fetch_contet_test_cases(contest)
    tasks = contest_test_cases.keys()

    for task in tasks:
        task_dir_name = contest_dir + task + '/'
        if not os.path.exists(task_dir_name):
            os.mkdir(task_dir_name)

        main_script_path = task_dir_name + 'main.py'
        if not os.path.exists(main_script_path):
            # 空のファイルを作成
            # TODO: テンプレートを用意してコピーする機能を追加
            main_script = pathlib.Path(main_script_path)
            main_script.touch()

        if not os.path.exists(task_dir_name + '/tests/'):
            os.mkdir(task_dir_name + '/tests/')
