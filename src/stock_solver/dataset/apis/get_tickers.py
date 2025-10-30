from argparse import ArgumentParser
from .alpaca import get_assets
from .alpha_vantage_calls import filter_tickers

parser = ArgumentParser()
parser.add_argument('--path', type=str, default='tickers',
                    help='File path for saving the list of tickers. Default is --path=tickers.')


def get_tickers(path: str):
    all_tickers = [asset.symbol for asset in get_assets()]
    filtered_tickers = filter_tickers(all_tickers)
    with open(path, 'w', encoding='utf-8') as save_file:
        save_file.writelines(filtered_tickers)
    save_file.close()


if __name__ == '__main__':
    args = parser.parse_args()
    get_tickers(args.path)
