from getpass import getpass
from bs4 import BeautifulSoup as bs
import requests
import pickle
import os

LOGIN_URL = 'https://atcoder.jp/login'


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


def save_cookies_in_local(cookies):
    """cookieをローカルに保存する
    '~/.pycoder' というディレクトリ内に 'cookies.jar' という名前でcookieを保存
    :param cookies
    """
    dir_path = os.environ['HOME'] + '/.pycoder'
    file_path = dir_path + '/cookies.jar'

    if not os.path.isdir(dir_path):
        os.mkdir(dir_path)

    # cookie.jarを保存
    with open(file_path, 'wb') as f:
        pickle.dump(cookies, f)


def load_cookies_in_local():
    """ログイン済みのcookiesを取り出す
    :return cookies_stored ログイン済みのcookies
    """
    dir_path = os.environ['HOME'] + '/.pycoder'
    file_path = dir_path + '/cookies.jar'

    cookies_stored = None
    with open(file_path, 'rb') as f:
        cookies_stored = pickle.load(f)
    return cookies_stored
