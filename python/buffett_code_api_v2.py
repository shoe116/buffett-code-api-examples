# ref: https://docs.python.org/3.8/howto/urllib2.html

import urllib.request
import json
import logging
import time
import sys
logging.basicConfig(stream=sys.stdout, level=logging.INFO)
LOGGER = logging.getLogger()


class BuffettCodeApiV2Client:
    BASE_URL = 'https://api.buffett-code.com/api/v2'

    def __init__(self, api_token: str):
        self._headers = {'x-api-key': api_token}

    def _get_json_data(self, url: str, params=None):
        if params:
            query_str = urllib.parse.urlencode(params)
            url = f'{url}?{query_str}'

        LOGGER.info(f'create request: url={url}')
        req = urllib.request.Request(url=url, headers=self._headers)
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read())

    def get_all_companies(self):
        url = f'{self.BASE_URL}/company'
        return self._get_json_data(url)

    def get_company(self, ticker):
        url = f'{self.BASE_URL}/company'
        return self._get_json_data(url, {'ticker': ticker})

    def get_quarter(self, ticker: str, fy: int, fq: int):
        url = f'{self.BASE_URL}/quarter'
        params = {
            'ticker': ticker,
            'fy': fy,
            'fq': fq,
        }
        return self._get_json_data(url, params)


def within_fixed_range(fy: int, fq: int, fixed_tier_range) -> bool:
    oldest_fy = int(fixed_tier_range['oldest_fiscal_year'])
    oldest_fq = int(fixed_tier_range['oldest_fiscal_quarter'])
    latest_fy = int(fixed_tier_range['latest_fiscal_year'])
    latest_fq = int(fixed_tier_range['latest_fiscal_quarter'])

    target_period = f'{fy}Q{fq}'
    oldest_period = f'{oldest_fy}Q{oldest_fq}'
    latest_period = f'{latest_fy}Q{latest_fq}'

    if target_period < oldest_period:
        return False
    elif latest_period < target_period:
        return False
    else:
        return True


if __name__ == '__main__':
    api_token = 'SET YOUR TOKEN'
    api_client = BuffettCodeApiV2Client(api_token)
    fy = 2018
    LOGGER.info('get all company data...')
    companies = api_client.get_all_companies()
    for key in companies:
        if key == 'column_description':
            LOGGER.info('this key is not ticker')
        else:
            ticker = key
            fixed_tier_range = companies[ticker][0]['fixed_tier_range']
            for fq in [1, 2, 3, 4]:
                if within_fixed_range(fy, fq, fixed_tier_range):
                    LOGGER.info(f'ticker={ticker} on {fy}Q{fq} is available')
                    quarter = api_client.get_quarter(ticker, fy, fq)
                    print(quarter[ticker])
                else:
                    LOGGER.info(f'ticker={ticker} on {fy}Q{fq} is out of fixed tier range. skip')
                time.sleep(0.5)