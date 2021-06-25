from getpass import getpass
from bs4 import BeautifulSoup as bs
import requests
from requests import Session
import pickle
import os
from typing import Optional
import datetime

from requests.sessions import RequestsCookieJar

LOGIN_URL = 'https://atcoder.jp/login'
PYCODER_DIR = os.environ['HOME'] + '/.pycoder'
COOKIES_PATH = PYCODER_DIR + '/cookies.jar'


def login():
    """ログインを行う
    ログインに成功した場合、cookieをローカルに保存する。
    """
    username, password = input_username_and_password()
    session = requests.session()
    csrf_token = get_csrf_token(LOGIN_URL, session)
    login_info = {
        'csrf_token': csrf_token,
        'username': username,
        'password': password,
    }
    res = session.post(LOGIN_URL, login_info, allow_redirects=False)
    # リダイレクト先が '/login' の場合、ログイン失敗
    if res.headers['location'] == '/login':
        print('Login failed...')
        exit(1)
    print('Login success!')
    save_cookies_in_local(res.cookies)


def logout():
    """ログアウトする。
    ローカルに保存したcookieを削除する
    """
    if os.path.exists(COOKIES_PATH):
        os.remove(COOKIES_PATH)
        print('You logout successfuly.')
    else:
        print('You have already logouted.')


def get_csrf_token(url: str, session):
    """csrfトークンを取得する.
    :param url: csrfトークンを取得したいページのurl
    :param session: session obj
    :return csrf_token
    """
    res = session.get(url)
    res.raise_for_status()
    html = res.text
    csrf_token = extract_csrf_token(html)
    return csrf_token


def input_username_and_password():
    """ユーザーネームとパスワードの入力を受け付ける
    :return username, password
    """
    username = input('username: ')
    password = getpass('password: ')
    return username, password


def extract_csrf_token(html: str) -> str:
    """htmlからcsrfトークンを取得する.
    :param html: csrfトークンを取得したいページ
    :return csrf_token
    """
    soup = bs(html, 'html5lib')
    csrf_token = soup.find(attrs={'name': 'csrf_token'}).get('value')
    return csrf_token


def save_cookies_in_local(cookies: RequestsCookieJar) -> None:
    """cookieをローカルに保存する
    '~/.pycoder' というディレクトリ内に 'cookies.jar' という名前でcookieを保存
    :param cookies
    """
    if not os.path.isdir(PYCODER_DIR):
        os.mkdir(PYCODER_DIR)

    # cookie.jarを保存
    with open(COOKIES_PATH, 'wb') as f:
        pickle.dump(cookies, f)


def load_cookies_in_local() -> Optional[RequestsCookieJar]:
    """ログイン済みのcookiesを取り出す
    :return cookies_stored ログイン済みのcookies
    """
    try:
        with open(COOKIES_PATH, 'rb') as f:
            cookies_stored: RequestsCookieJar = pickle.load(f)
        return cookies_stored
    except FileNotFoundError as e:
        print('Local cookies does not exist.')
        print('Please login.')
        return None


def _get_last_modified_date_of_cookies():
    t = os.path.getmtime(COOKIES_PATH)
    return datetime.datetime.fromtimestamp(t)


def cookie_is_expired():
    """ローカルに保存したcookieの経過時間をチェックする。
    7日以上の場合を期限切れと判定する。
    :return 期限切れかどうか
    """
    last_modified_date = _get_last_modified_date_of_cookies()
    elapsed_time = (datetime.datetime.now() - last_modified_date).seconds
    max_time = 60*60*24*7
    return elapsed_time > max_time


def check_cookies() -> Optional[Session]:
    """ログイン状態かどうかを確認する。
    ログイン済みであれば、cookieを更新する。
    ログインしていない場合、ログインの必要ありとメッセージを出す。
    """
    # cookieの期限が切れていなければ再利用する
    if cookie_is_expired():
        print('Cookie is expired.')
        return None
    else:
        # Load stored cookies
        cookies_stored = load_cookies_in_local()
        if not cookies_stored:
            print('not logined...')
            return None

        # Set cookies
        session = requests.session()
        session.cookies.update(cookies_stored)
        return session

def check_login() -> Optional[Session]:
    """ログイン状態かどうかを確認する。
    ログイン済みであれば、cookieを更新する。
    ログインしていない場合、ログインの必要ありとメッセージを出す。
    """

    # Load stored cookies
    cookies_stored = load_cookies_in_local()
    if not cookies_stored:
        print('not logined...')
        return None

    # Set cookies
    session = requests.session()
    session.cookies.update(cookies_stored)

    # 提出ページにアクセスできるかどうかでログイン状態を判定
    url = 'https://atcoder.jp/contests/abc001/submit'
    res = session.get(url, allow_redirects=False)

    if res.status_code != 302:
        print('logined!')
        # update cookies
        save_cookies_in_local(res.cookies)
        return session
    else:
        print('not logined...')
        return None


def auth(func):
    """認証チェックを行うデコレータ
    デコレートした関数の第一引数にログイン済みのセッションを渡す
    """
    def decorator(*args, **kargs):
        print('auth decorator called.')
        session_logined = check_cookies()

        if session_logined:
            ret = func(session_logined, *args, **kargs)
            # update cookies
            save_cookies_in_local(session_logined.cookies)
            return ret
        else:
            print('Please login.')
            exit(1)

    return decorator
