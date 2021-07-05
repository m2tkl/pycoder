from typing import Dict
from . import scrape
from .scrape import SampleTestCases
import os
import pathlib
import shutil


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

    # 問題ごとのサブディレクトリを作成
    for task in contest_test_cases.keys():
        task_dir_name = contest_dir + task + '/'
        if not os.path.exists(task_dir_name):
            os.mkdir(task_dir_name)

        # 問題解答スクリプト用にテンプレートファイルをコピー
        main_script_path = task_dir_name + 'main.py'
        if not os.path.exists(main_script_path):
            template_path = './atcoder/templates/default.py'
            shutil.copy(template_path, main_script_path)

        # テスト用のディレクトリを作成
        if not os.path.exists(task_dir_name + '/tests/'):
            os.makedirs(task_dir_name + '/tests/')

    # 取得したテストケースを格納する
    for task_name, test_cases in contest_test_cases.items():
        for test_number, test_case in test_cases.items():
            task_test_dir = contest_dir + task_name + '/tests/' + str(test_number) + '/'
            os.mkdir(task_test_dir)
            with open(task_test_dir + 'in.txt', 'w') as f:
                f.write(test_case.input)
            with open(task_test_dir + 'out.txt', 'w') as f:
                f.write(test_case.output)


def init():
    """atcoder用のディレクトリを作成する
    """
    base_dir = './atcoder/'
    if not os.path.exists(base_dir):
        os.mkdir(base_dir)

    contests_dir = base_dir + 'contests/'
    if not os.path.exists(contests_dir):
        os.mkdir(contests_dir)

    templates_dir = base_dir + 'templates/'
    if not os.path.exists(templates_dir):
        os.mkdir(templates_dir)

    template_file = templates_dir + 'default.py'
    if not os.path.exists(template_file):
        default_template = pathlib.Path(template_file)
        default_template.touch()
