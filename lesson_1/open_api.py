"""
2. Изучить список открытых API (https://www.programmableweb.com/category/all/apis).
Найти среди них любое, требующее авторизацию (любого типа).
Выполнить запросы к нему, пройдя авторизацию. Ответ сервера записать в файл.
"""
import requests


def load_most_popular_track(api_key):
    try:
        url = "http://ws.audioscrobbler.com/2.0/"

        response = requests.get(url, params={'method': 'chart.gettoptracks',
                                             'api_key': api_key,
                                             'format': 'json'})

        data = response.json()

        tracks = data.get('tracks').get('track')

        most_popular_tracks = [(f'{i} место', track.get('name')) for i, track in enumerate(tracks, start=1)]

        with open('most_popular_tracks.txt', 'w', encoding='UTF-8') as file:
            for track in most_popular_tracks:
                file.writelines(f"{' - '.join(track)}\n")

        return 'Load most popular tracks is successfully'

    except Exception as e:
        return f'Upps... something went wrong, check connections please'


def main():
    api_key = 'c8a1be15db3768e310a3c5a8cd4c9347'
    print(load_most_popular_track(api_key))


if __name__ == '__main__':
    main()
