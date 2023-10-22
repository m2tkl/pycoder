from typing import Dict, Mapping, NamedTuple, NewType, Optional, cast
from requests import Session
from bs4 import BeautifulSoup as bs
from .auth import auth


ATCODER_URL = 'https://atcoder.jp'
CONTEST_URL = 'https://atcoder.jp/contests/'


ContestTasksPage = NewType('ContestTasksPage', str)
ProbPaths = NewType('ProbPaths', Dict[str, str])
ProbUrls = NewType('ProbUrls', Dict[str, str])


class TestCase(NamedTuple):
    input: str
    output: str


SampleTestCases = NewType('SampleTestCases', Dict[int, Optional[TestCase]])


def _get_tasks_url(contest: str) -> str:
    return CONTEST_URL + contest + '/tasks'


@auth
def fetch_contest_tasks_page(session_logined: Session, contest: str) -> ContestTasksPage:
    """問題一覧ページのhtmlを取得する.
    :param conteste コンテスト(ex: abc123)
    :return html コンテスト問題一覧ページのhtml
    """
    tasks_url = _get_tasks_url(contest)
    res = session_logined.get(tasks_url)
    html = cast(ContestTasksPage, res.text)
    return html


def extract_prob_paths(html: ContestTasksPage) -> ProbPaths:
    """問題一覧ページから各問題へのパスを取得する.
    :param html 問題一覧ページ
    :return prob_paths 各問題のパス
    """
    soup = bs(html, 'html5lib')
    prob_paths = cast(ProbPaths, {})
    for tr in soup.find('tbody').find_all('tr'):
        item = tr.find('td').find('a')
        p_type = item.contents[0].lower()
        link = item.get('href')  # ex: /contests/abc160/tasks/abc160_a
        prob_paths[p_type] = link
    return prob_paths


def get_task_screen_name(prob_paths: ProbPaths, prob_type: str) -> str:
    """コンテスト問題一覧ページからprob_typeで指定された問題の名前を取得する。
    :param prob_paths
    :param prob_type 問題のタイプ(a,b,c,...)
    :return task_screen_name 問題の名前
        ex: abc160_a
        !! 必ずしもコンテスト番号、問題のタイプと、
        取得するtask_screen_nameは一致しない。
        例えば、abc123のa問題のtask_screen_nameがarc012_bということがある。
    """
    # /contests/abc160/tasks/abc160_a から
    # 最後の'abc160_a'の部分を取り出す
    return prob_paths[prob_type].split('/')[-1]


def prob_paths_to_urls(prob_paths: ProbPaths) -> ProbUrls:
    """コンテスト問題一覧ページ(tasksページ)から各問題のurlを取得して返す
    :param html コンテストのtasksページ
    :return prob_paths 各問題へのurlを持つdict
    """
    prob_urls = cast(ProbUrls, prob_paths.copy())
    for prob_type, link in prob_paths.items():
        prob_urls[prob_type] = ATCODER_URL + link
    return prob_urls


def extract_sample_test_cases_from_prob_page(html: str) -> SampleTestCases:
    """問題ページからサンプルテストケースを抽出する.
    :param html 問題ページ
    :return 問題ページのサンプルテストケース.
        {0: (入力例1, 出力例1), 1: (入力例2, 出力例2), ...}といった形式の辞書で返す.
    """
    soup = bs(html, 'html5lib')

    # 英語ページを除外（日本語ページのサンプルケースと重複して取得してしまうのを防ぐため）
    while soup.find('span', class_='lang-en'):
        soup.find('span', class_='lang-en').extract()

    # 入出力の形式欄を除外
    while soup.find('div', class_='io-style'):
        soup.find('div', class_='io-style').extract()

    io_samples = []
    for sec in soup.find_all('section'):
        if sec.find('h3').get_text() == '問題文':
            continue
        # section内の先頭以外のpreは'間違いの例'などサンプルケースでないことがあるため、
        # 先頭のpreのみを取得する
        pre = sec.find('pre')
        if pre is None:
            continue
        io_samples.append(pre.get_text())

    sample_test_cases = cast(SampleTestCases, {})
    for i in range(0, len(io_samples), 2):
        try:
            sample_test_cases[(i//2)+1] = TestCase(io_samples[i],
                                                   io_samples[i+1])
        except IndexError:
            sample_test_cases[(i//2)+1] = None

    return sample_test_cases


@auth
def fetch_sample_test_cases(session_logined: Session, prob_urls: ProbUrls):
    """
    """
    contest_sample_test_cases = {}
    for prob_type, prob_url in prob_urls.items():
        res = session_logined.get(prob_url)
        sample_test_cases = extract_sample_test_cases_from_prob_page(res.text)
        contest_sample_test_cases[prob_type] = sample_test_cases
    return contest_sample_test_cases
