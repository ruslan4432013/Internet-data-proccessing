"""
1. Посмотреть документацию к API GitHub,
разобраться как вывести список репозиториев для конкретного пользователя,
сохранить JSON-вывод в файле *.json.
"""
import requests
import json


class GitInfo:
    def __init__(self, name):
        self.name = name
        self.__url = f"https://api.github.com/users/{self.name}/repos"

    def save_repo_list_in_json(self, file_name):
        try:
            response = requests.get(self.__url)
            data = response.json()
            list_repos = [repo.get('name') for repo in data]
            with open(f'{file_name}.json', 'w') as f:
                json.dump(list_repos, f)

            return f'Loading list repos to {file_name}.json is done'

        except Exception as e:
            return 'Check your connection please or username'


def main():
    user = 'ruslan4432013'
    repos = GitInfo(user)
    print(repos.save_repo_list_in_json('my_repos'))


if __name__ == '__main__':
    main()
