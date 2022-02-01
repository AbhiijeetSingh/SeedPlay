import json
import requests
from bs4 import BeautifulSoup
from InquirerPy import inquirer
import os


def get_files(session, url):
    r = session.get(url)
    return parse_files(session, r.text, url)


def parse_files(session, files, url):
    videos = []
    folders = []
    soup = BeautifulSoup(files, "html.parser")
    for link in soup.find_all("a"):
        if link.get("href")[-1] == "/":
            folders.append(link.get("href"))
        elif link.get("href")[-5:] != ".meta":
            videos.append(link.get("href"))

    return videos, folders


def select_file(session, videos, folders, url):
    action = inquirer.select(message="Select an option",
                             choices=videos + folders, default=None).execute()
    if action in videos:
        return f"{url}/{action}"
    if action in folders:
        url = f"{url}/{action[0:-1]}"
        videos, folders = get_files(session, url=(url))
        action = select_file(session, videos, folders, url)
        return f"{action}"


def get_credentials():
    with open("config.json", "r") as config_file:
        config = json.load(config_file)
        username = config["username"]
        password = config["password"]
        return username, password


def play_media(url):
    os.system(f"mpv --keep-open=yes {url}")


def main():
    print("SeedPlay")
    username, password = get_credentials()
    files_address = f"https://{username}:{password}@{username}.seedbox.io/files"

    session = requests.Session()
    videos, folders = get_files(session, files_address)

    media_url = select_file(session, videos, folders, url=files_address)
    play_media(url=media_url)


main()
