import re
from appdirs import user_config_dir
from argparse import ArgumentParser
from datetime import timedelta
from json import dumps
from loguru import logger
from requests_cache import CachedSession
USERAGENT = 'illallangi-telegraf-stockdata'

# Source: https://djangosnippets.org/snippets/585/
camelcase_to_underscore = (
    lambda str: re.sub("(((?<=[a-z])[A-Z])|([A-Z](?![A-Z]|$)))", "_\\1", str)
    .lower()
    .strip("_")
)

def process(
    apikey,
    json,
    measurement,
    tickers,
    baseurl = 'https://api.stockdata.org/v1/'
):
    with CachedSession(
        user_config_dir(USERAGENT),
        cache_control=False,
        expire_after=timedelta(minutes=20),
        allowable_methods=[
            "GET",
        ],
        backend="filesystem",
    ) as session:
        n = 3
        for symbols in [tickers[i:i + n] for i in range(0, len(tickers), n)]:
            get = {
                'url': f'{baseurl}/data/quote?api_token={apikey}&symbols={",".join(symbols)}',
                "headers": {
                    "User-Agent": USERAGENT,
                },
            }
            logger.trace(get)
            response = session.get(**get)
            response.raise_for_status()
            assert response.status_code == 200, f'Unexpected response code {response.status_code}, expected 200'
            assert response.headers['Content-Type'] == 'application/json', f"Unexpected content-type {response.headers['Content-Type']}, expected application/json"
            result = response.json()
            logger.trace(result)
            assert 'meta' in result, f"Response does not contain meta"
            assert 'data' in result, f"Response does not contain data"
            assert result['meta']['returned'] == len(symbols), f"Requested {len(symbols)} tickers, but only received {result['meta']['returned']}"

            for payload in result['data']:
                tags, fields = convert(payload)
                if json:
                    print(dumps({'measurement': measurement, 'tags': tags, 'fields': fields}))
                else:
                    print(
                        f"{measurement},{','.join([f'{k}={v}' for k, v in tags.items()])} {','.join([f'{k}={v}' for k, v in fields.items()])}"
                    )



            # print(response.from_cache)
            # print(response.expires)
            # print(response.json()['data'])

def convert(payload=None):
    tags = {}
    fields = {}

    for k in payload:
        v = payload[k]
        converted_key = camelcase_to_underscore(k)
        converted_value = None

        try:
            converted_value = float(v)
        except ValueError:  # All string values become tags
            tags[converted_key] = v.replace(' ', '\ ').replace(',','\,')
        except TypeError:  # All null values are ignored
            pass
        if converted_value:
            fields[converted_key] = converted_value
    return (tags, fields)

if __name__ == "__main__":
    parser = ArgumentParser(
        description="Retrieves stock information from StockData.org and formats them in InfluxDB line format."
    )
    parser.add_argument(
        "--apikey", required=True, help="StockData.org api key"
    )
    parser.add_argument(
        "--json", action="store_true", help="Output in JSON instead of InfluxDB"
    )
    parser.add_argument(
        "--measurement", default="stocks", help="Measurement name for InfluxDB."
    )
    parser.add_argument(
        "--tickers", required=True, help="Comma-separated ticker symbols to check on Yahoo Finance."
    )
    args = parser.parse_args()
    try:
        process(
            apikey=args.apikey,
            json=args.json,
            measurement=args.measurement,
            tickers=args.tickers.split(','),
        )
    except Exception as e:
        print(e)
