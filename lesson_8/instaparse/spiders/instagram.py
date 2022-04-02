import re
import json

import scrapy
from scrapy.http import HtmlResponse
from instaparse.items import InstaparseItem


class InstagramSpider(scrapy.Spider):
    name = 'instagram'
    allowed_domains = ['instagram.com']
    start_urls = ['https://www.instagram.com/']
    login_url = 'https://www.instagram.com/accounts/login/ajax/'
    inst_pwd = '#PWD_INSTAGRAM_BROWSER:10:1648880590:AZhQAFJ57Mo5e1MOlfqZQPWgwv/D9NSRuMHv48IzMxnfUUYO0FG2iq6nGtF8PcL7MkQrbieTxismLy0anzf78eFAxeBCg7kyqISPJ4sMg8JtEi/TUnVcEHi7+BCy6cEpW4YgAVIw18a1Kd5DKHs='
    inst_login = 'ruslan4432013@gmail.com'
    users_for_parse = ['ivan_pestretsov_', 'flafik_mari']
    inst_user_followers_url = 'https://i.instagram.com/api/v1/friendships/{user_id}/followers/'
    inst_user_subscribers_url = 'https://i.instagram.com/api/v1/friendships/{user_id}/following/'
    inst_links = [inst_user_followers_url, inst_user_subscribers_url]

    def parse(self, response: HtmlResponse, **kwargs):
        csrf_token = self.fetch_csrf_token(response.text)

        yield scrapy.FormRequest(
            self.login_url,
            method='POST',
            callback=self.login,
            formdata={'username': self.inst_login,
                      'enc_password': self.inst_pwd},
            headers={'X-CSRFToken': csrf_token},
        )

    def login(self, response: HtmlResponse):
        j_data = response.json()
        if j_data['authenticated']:
            for user_for_parse in self.users_for_parse:
                yield response.follow(f'/{user_for_parse}',
                                      callback=self.user_data_parse,
                                      cb_kwargs={'username': user_for_parse})


    def user_data_parse(self, response: HtmlResponse, username):
        user_data = self.fetch_user_id_user_name(response.text)
        user_id = user_data.get('id')
        for link in self.inst_links:
            max_id = 12
            url_to_get_info = f'{link.format(user_id=user_id, max_id=max_id)}'
            yield response.follow(url_to_get_info,
                                  callback=self.user_post_parse,
                                  cb_kwargs={'username': username,
                                             'user_id': user_id},
                                  headers={'User-Agent': 'Instagram 155.0.0.37.107'})

    def user_post_parse(self, response: HtmlResponse, username, user_id):
        data = response.json()
        next_max_page = data.get('next_max_id', None)
        if next_max_page:
            url_to_get = f'{self.inst_user_subscribers_url.format(user_id=user_id)}?count=12&max_id={next_max_page}'
            if 'followers' in response.url:
                url_to_get = f'{self.inst_user_followers_url.format(user_id=user_id)}?count=12&max_id={next_max_page}&search_surface=follow_list_page'

            yield response.follow(url_to_get,
                                  callback=self.user_post_parse,
                                  cb_kwargs={'username': username,
                                             'user_id': user_id},
                                  headers={'User-Agent': 'Instagram 155.0.0.37.107'})

        user_list = data.get('users')
        for user in user_list:
            item = InstaparseItem(
                username=user.get('username', None),
                main_user=username,
                followers=True if 'followers' in response.url else False,
                full_name=user.get('full_name', None),
                user_id=user.get('pk', None),
                photo=user.get('profile_pic_url', None),
            )
            yield item

    def fetch_csrf_token(self, text):
        matched = re.findall(r'"csrf_token":"(.*?)"', text)
        if matched:
            return matched[0]

    def fetch_user_id_user_name(self, text):
        """return dict with keys 'id' and 'username' """
        matched = re.findall(r'"owner":{(.*?)}', text)
        j_data = json.loads('{%s}' % matched[0])
        return j_data
