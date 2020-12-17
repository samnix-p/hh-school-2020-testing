import json
import os

import requests


def pretty_json(js):
    return json.dumps(js, indent=4, sort_keys=True)


def print_result(func):
    def wrapper(*args, **kwargs):
        print("TEST OK" if func(*args, **kwargs) else "TEST FAIL")
    return wrapper


class ApiTesting:
    def __init__(self):
        self.hh_domain = 'https://api.hh.ru/'
        self.headers = {
            'Host': 'api.hh.ru',
            'Authorization': f'Bearer {os.environ["HH_TOKEN"]}'
        }

    @staticmethod
    def print_status(r, message):
        print('  ', end='')
        if r.status_code == 200:
            print(message)
            return True
        else:
            print(pretty_json(r.json()))
            return False

    @staticmethod
    def has_vacancy(r):
        if r.json()['found'] != 0:
            return True
        else:
            return False

    def check_connection(self):
        print('Checking connection')
        r = requests.get(f'{self.hh_domain}me', headers=self.headers)

        return self.print_status(r, 'Connection is OK')

    @print_result
    def check_empty_string(self):
        print('Checking empty string')
        payload = {
            'text': ''
        }
        r = requests.get(f'{self.hh_domain}vacancies', headers=self.headers, params=payload)

        return self.print_status(r, 'Vacancies found = {}'.format(r.json()['found']))

    @print_result
    def check_the_string(self):
        search_word = 'Программист'
        print('Checking {} string'.format(search_word))
        payload = {
            'text': '{}'.format(search_word)
        }
        r = requests.get(f'{self.hh_domain}vacancies', headers=self.headers, params=payload)
        print('  ', end='')
        if search_word in r.text:
            print('Found {} in response'.format(search_word))
        else:
            print("Couldn't find {} in response".format(search_word))
        return self.print_status(r, 'Vacancies found = {}'.format(r.json()['found']))

    @print_result
    def check_n_symbols_string(self, N):
        print('Checking {} symbols string'.format(N))
        payload = {
            'text': 'a'*N
        }
        r = requests.get(f'{self.hh_domain}vacancies', headers=self.headers, params=payload)
        found_vacancies = r.json()['found']
        self.print_status(r, 'Vacancies found = {}'.format(found_vacancies))

        if (N > 255 and found_vacancies > 0) or (N < 256 and found_vacancies == 0):
            return True
        else:
            return False

    @print_result
    def check_special_string(self, search_word, valid=True, log=False):
        print('Checking !"{}" string'.format(search_word))
        payload = {
            'text': '!"{}"'.format(search_word)
        }
        r = requests.get(f'{self.hh_domain}vacancies', headers=self.headers, params=payload)

        if log:
            print(r.text)

        print('  ', end='')
        if search_word in r.text:
            print('Found {} in response'.format(search_word))
        else:
            print("Couldn't find {} in response".format(search_word))

        self.print_status(r, 'Vacancies found = {}'.format(r.json()['found']))
        if (self.has_vacancy(r) and valid) or (not self.has_vacancy(r) and not valid):
            return True
        else:
            return False


def main():
    at = ApiTesting()
    at.check_connection()

    print('')
    print('--- Basic check --- ')
    at.check_empty_string()
    at.check_the_string()

    print('')
    print('--- Edges check --- ')
    at.check_n_symbols_string(254)
    at.check_n_symbols_string(255)
    at.check_n_symbols_string(256)

    print('')
    print('--- Search query !"{search_word}" --- ')
    print('Valid string')
    at.check_special_string('Программист')
    print('Invalid string')
    at.check_special_string('авыпывап', False)

    print('')
    print('--- Search query !"{word1 word2}" --- ')
    print('Valid string')
    at.check_special_string('Разработчик ПО')
    print('Invalid string (with typo)')
    at.check_special_string('ПО разрааботчик', False)


if __name__ == '__main__':
    main()
