import configparser
import os

from ddl import *
from dateutil import parser
from typing import Dict
from mail_alert import send_email
import pytz
import requests
import logging
import logging.handlers

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger_file_handler = logging.handlers.RotatingFileHandler(
    "status.log",
    maxBytes=1024 * 1024,
    backupCount=1,
    encoding="utf8",
)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger_file_handler.setFormatter(formatter)
logger.addHandler(logger_file_handler)

EPIC_API: str = "https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions"

PARAMS: Dict[str, str] = {
    "locale": "en-US",
    "country": "US",
    "allowCountries": "US",
}

user_name = os.environ["Sender_Name"]


def msg_body_gen(games_table):
    msg_body = f"""
        <html>
        <body>
        <p>
        Hi {user_name},
        </p>
        <p>
        These are the below games that are available to download for free in Epic Games Store.
        </p>
        <br/>
        <table border="4">
            <tr>
                <th>
                    Image
                </th>
                 <th>
                    Title
                </th>
                <th>
                    Offer Start Date
                </th>
                <th>
                    Offer End Date
                </th>
                 <th>
                    Claim URL
                 </th>
            </tr>
            {games_table}
        </table>
        <br/>
        <p>
        Regards,
        </p>
        Automation Bot
        </body>
        </html>
        """
    return msg_body


def get_free_epic_games():
    response = requests.get(EPIC_API, params=PARAMS)
    tables_html = ""
    config_parser = configparser.ConfigParser()
    config_parser.read("config.ini")
    time_zone = config_parser["TIMEZONE"]["timezone"]
    local_tz = pytz.timezone(time_zone)

    for game in response.json()["data"]["Catalog"]["searchStore"]["elements"]:
        game_name = game["title"]
        if game_name not in get_alerted_games():
            if len(game["promotions"]["promotionalOffers"]) != 0:
                start_date = parser.parse(
                    game["promotions"]["promotionalOffers"][0]["promotionalOffers"][0]['startDate'])
                start_date = start_date.replace(tzinfo=pytz.utc).astimezone(local_tz)
                start_date = start_date.strftime("%Y-%m-%d %I:%M:%S %p")

                end_date = parser.parse(
                    game["promotions"]["promotionalOffers"][0]["promotionalOffers"][0]['endDate'])
                end_date = end_date.replace(tzinfo=pytz.utc).astimezone(local_tz)
                end_date = end_date.strftime("%Y-%m-%d %I:%M:%S %p")

                game_img = game["keyImages"][-1]['url']

                try:
                    game_url = f'<a href = "https://www.epicgames.com/en-US/p/{game["productSlug"]}"> Claim Now </a>'
                except KeyError as e:
                    game_url = f'URL NOT AVAILABLE.'

                tables_html += f"""
                                <tr>
                                    <td>
                                        <img src="{game_img}" height="150" width="100">
                                    </td>
                                    <td>
                                        {game_name}
                                    </td>
                                     <td>
                                        {start_date}
                                    </td>
                                    <td>
                                        {end_date}
                                    </td>
                                     <td>
                                        {game_url}
                                     </td>
                                </tr>
                                """
                insert_query(game_name)
                logger.info(f'Title: {game_name} Offer Start: {start_date} Offer End: {end_date}')
            else:
                logger.info(f'Title: {game_name} Not A Free Game.')
                continue
        else:
            logger.info(f'Title: {game_name} Already Sent Alert.')
            continue

    if tables_html != "":
        print("Sending Mail")
        send_email(os.environ["Receiver_Email"], "[Epic Games Store] Free Games", msg_body_gen(tables_html))


get_free_epic_games()
