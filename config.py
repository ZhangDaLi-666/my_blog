import os
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 3306)),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'shxj_news'),
    'charset': 'utf8mb4'
}

SITE_ROOT = 'http://www.shxj.edu.cn'
BASE_URL = f'{SITE_ROOT}/xxgk/342/list.htm'
PAGE_URL_TEMPLATE = f'{SITE_ROOT}/xxgk/342/list{{page}}.htm'

REQUEST_DELAY = float(os.getenv('REQUEST_DELAY', '1.0'))

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
