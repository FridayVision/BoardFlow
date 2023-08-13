from lxml import etree
import requests
import pandas as pd
import xml.etree.ElementTree as ET
from ratelimit import limits, sleep_and_retry
from tenacity import retry, stop_after_attempt, wait_random_exponential, wait_fixed

from dagster import asset

# TODO: Add logs

@retry(stop=stop_after_attempt(3), wait=wait_fixed(5))
def fetch_bgg_xml_data(game_id):
    base_url = 'https://www.boardgamegeek.com/xmlapi2/thing?id='
    url = base_url + str(game_id) + "&ratingcomments=0&stats=1"

    response = requests.get(url)

    if response.status_code == 200:
        return response.content
    else:
        # print(response.status_code)
        raise Exception(f"Error fetching XML data from BGG for game id={game_id}.")


def parse_ranks(ranks_element):
    ranks_list = []
    for rank_element in ranks_element.findall('rank'):
        rank_info = {
            'type': rank_element.attrib['type'],
            'id': str(rank_element.attrib['id']),
            'name': rank_element.attrib['name'],
            'friendlyname': rank_element.attrib['friendlyname'],
            'value': str(rank_element.attrib['value']),
            'bayesaverage': str(rank_element.attrib['bayesaverage']),
        }
        ranks_list.append(rank_info)
    return ranks_list


def parse_bgg_xml(xml_data):
    root = ET.fromstring(xml_data)

    boardgame_info = {}
    item = root.find(".//item[@type='boardgame']")
    if item:
        # Extract attributes
        boardgame_info['Name'] = root.find(".//name[@type='primary']").attrib['value']
        boardgame_info['Description'] = root.find(".//description").text.strip()
        boardgame_info['MinPlayers'] = str(root.find(".//minplayers").attrib['value'])
        boardgame_info['MaxPlayers'] = str(root.find(".//maxplayers").attrib['value'])
        boardgame_info['YearPublished'] = str(root.find(".//yearpublished").attrib['value'])
        boardgame_info['PlayingTime'] = str(root.find(".//playingtime").attrib['value'])

        # Extract board game categories
        boardgame_info['BoardGameCategories'] = [cat.attrib['value'] for cat in
                                                 root.findall(".//link[@type='boardgamecategory']")]

        # Extract board game mechanics
        boardgame_info['BoardGameMechanics'] = [mech.attrib['value'] for mech in
                                                root.findall(".//link[@type='boardgamemechanic']")]

        # Extract board game families
        boardgame_info['BoardGameFamilies'] = [family.attrib['value'] for family in
                                               root.findall(".//link[@type='boardgamefamily']")]

        # Extract statistics
        boardgame_info['Ratings'] = {}
        ratings = root.find(".//statistics/ratings")
        boardgame_info['Ratings']['UsersRated'] = str(ratings.find("usersrated").attrib['value'])
        boardgame_info['Ratings']['AverageRating'] = str(ratings.find("average").attrib['value'])
        boardgame_info['Ratings']['BayesAverageRating'] = str(ratings.find("bayesaverage").attrib['value'])

        # Extract Rank
        ranks_element = ratings.find(".//ranks")
        if ranks_element is not None:
            boardgame_info['game_rank'] = parse_ranks(ranks_element)

        return boardgame_info
    return "Invalid ID"

@asset
def pull_data_test():
    results = []

    for game_id in range(1, 30):
        if game_id % 10 == 0:
            print("Successful on {} Requests".format(game_id))
        xml_data = fetch_bgg_xml_data(game_id)
        boardgame_info = parse_bgg_xml(xml_data)
        results.append(boardgame_info)

    filtered_data_list = [item for item in results if isinstance(item, dict)]
    df = pd.DataFrame(filtered_data_list)
    df.to_csv('/Users/derinben/PycharmProjects/BoardFlow/dagster_src/data_test.csv', index = False)

    return "Run Success"
