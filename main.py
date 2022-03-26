from email.mime import base
import json
import requests
from bs4 import BeautifulSoup
from InquirerPy import inquirer
import os
from urllib.parse import unquote_plus


def parse_files(files):
    videos = []
    folders = []
    soup = BeautifulSoup(files, "html.parser")
    for link in soup.find_all("a"):
        if link.get("href")[-1] == "/":
            folders.append(Directory(link.get("href")))
        elif link.get("href")[-5:] != ".meta":
            videos.append(DirectoryEntry(link.get("href")))

    videos.sort(key=lambda x: x.url)
    folders.sort(key=lambda x: x.url)
    return videos, folders


def get_files(session, url):
    r = session.get(url)
    return parse_files(r.text)


class DirectoryEntry(object):
    def __init__(self, url) -> None:
        self.url = url

    def __str__(self):
        return unquote_plus(self.url)

    def __repr__(self):
        return f"DirectoryEntry<Url={str(self)}"


class Directory(DirectoryEntry):
    def __init__(self, url) -> None:
        if not url.endswith("/"):
            url = url + "/"
        super().__init__(url)

    def __repr__(self):
        return f"Directory<Url={str(self)}"


class FileNavigator(object):
    def __init__(self, base_url, session) -> None:
        self.__current_dir_url = base_url
        self.__base_url = base_url
        self.__session = session
        self.__current_dir_files = []
        self.__current_dir_sub_dirs = []
        self.change_dir(Directory(""))

    def current_dir_contents(self):
        return self.__current_dir_files + self.__current_dir_sub_dirs

    def get_current_dir_url(self):
        return self.__current_dir_url

    def change_dir(self, dir: Directory):
        self.__current_dir_url = self.__current_dir_url + dir.url
        self.__current_dir_files, self.__current_dir_sub_dirs = get_files(
            self.__session, self.__current_dir_url)

    def get_files(self):
        return self.__current_dir_files

    def get_sub_dirs(self):
        return self.__current_dir_sub_dirs

    def get_base_url(self):
        return self.__base_url


def select_file(session, videos, folders, url):
    action = inquirer.select(message="Select an option",
                             choices=videos + folders, default=None).execute()
    if action in videos:
        return f"{url}/{action.url}"
    if action in folders:
        os.system("cls")
        url = f"{url}/{action.url[0:-1]}"
        videos, folders = get_files(session, url=(url))
        action = select_file(session, videos, folders, url)
        return f"{action}"


def get_credentials():
    with open(".\config.json", "r") as config_file:
        config = json.load(config_file)
        username = config["username"]
        password = config["password"]
        return username, password


def play_loop(nav: FileNavigator):
    selection = inquirer.select(
        message="Select an option", choices=nav.current_dir_contents(), default=None).execute()

    while isinstance(selection, Directory):
        os.system("cls")
        nav.change_dir(selection)
        selection = inquirer.select(
            message="Select an option", choices=nav.current_dir_contents(), default=None).execute()
    play_media(nav.get_current_dir_url() + selection.url)


def play_media(url):
    os.system(f"mpv --keep-open=yes {url}")
    os.system("cls")


def main():
    os.system("cls")
    print("SeedPlay")
    username, password = get_credentials()
    files_address = f"https://{username}:{password}@{username}.seedbox.io/files/"

    session = requests.Session()
    nav = FileNavigator(
        files_address, session)

    while True:
        try:
            play_loop(nav)
        except KeyboardInterrupt:
            os.system("cls")
            print("Exiting...")
            break


main()
