from enum import Enum

API_BASE = "https://zno.osvita.ua/"
# TODO(Vasyl): Add CLI parameter to omit scrapping step
SHOULD_SCRAPE_OSVITA_UA = True


class Formats(Enum):
    HTML = "html"
    RAW = "raw"
    MARKDOWN = "md"
