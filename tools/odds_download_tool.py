import os
from smolagents import tool
import requests

@tool
def odds_download_tool() -> (str|None):
    """
    This is a tool that downloads the odds from the NRL website.

    Args:
        None
    """

    try:
        if os.environ.get("ODDS_PORTAL_URL") is None:
            raise ValueError("ODDS_PORTAL_URL not set in environment variables")

        if os.environ.get("ODDS_PORTAL_KEY") is None:
            raise ValueError("ODDS_PORTAL_KEY not set in environment variables")

        url = (os.environ.get("ODDS_PORTAL_URL") or "") + (os.environ.get("ODDS_PORTAL_KEY") or "")
        response = requests.get(url)
        data = response.json()

        return data

    except Exception as e:
        print(e)
        return None
