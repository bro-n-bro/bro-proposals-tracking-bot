from data.config import NETWORKS
from sql import save_to_db, create_table, check_dublicates, set_option
from _wallet import address_to_address
from dateutil import parser
from itertools import chain

import aiohttp
import asyncio
import time
import logging


logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)


async def get_proposals(session, network):
    url = f"{network['lcd_api']}/cosmos/gov/v1beta1/proposals?proposal_status=2&pagination.limit=100"
    async with session.get(url) as resp:
        resp = await resp.json()
        props = [prop for prop in resp['proposals'] if prop['status'] == 'PROPOSAL_STATUS_VOTING_PERIOD']
        return [parse_proposal(network, prop) for prop in props]


async def get_vote(session, proposal):
    network = [network for network in NETWORKS if network['name'] == proposal[0]][0]
    voter = address_to_address(network['validator'], network['prefix'])
    url = f"{network['lcd_api']}/cosmos/gov/v1beta1/proposals/{proposal[1]}/votes/{voter}"
    async with session.get(url) as resp:
        resp = await resp.json()
        if 'code' in list(resp.keys()):
            proposal.append(False)
            return proposal
        else:
            set_option(network['name'], proposal[1], True)
            return None


async def get_votes(session, proposals):
    tasks = []
    for p in proposals:
        tasks.append(asyncio.ensure_future(get_vote(session, p)))
    proposals = await asyncio.gather(*tasks)
    return proposals


async def get_data():
    async with aiohttp.ClientSession() as session:
        tasks = []
        for network in NETWORKS:
            tasks.append(asyncio.ensure_future(get_proposals(session, network)))
        proposals = await asyncio.gather(*tasks)
        proposals = list(chain.from_iterable(proposals))
        proposals = [p for p in proposals if p and p != []]
        proposals = await get_votes(session, proposals)
        for p in proposals:
            if p:
                p.extend([int(time.time()) + 15, 0])
            else:
                continue
        [save_to_db(p) for p in proposals if p and not check_dublicates(p[0], p[1])]
        logging.info("Data saved in a database")


def parse_proposal(network, proposal: dict):
    network = network['name']
    try:
        _id = int(proposal['id'])
    except Exception as e:
        _id = int(proposal['proposal_id'])
    try:
        title = proposal['content']['value']['title']
    except KeyError:
        title = proposal['content']['title']
    voting_end_time = int(parser.parse(proposal['voting_end_time']).timestamp())
    return [network, _id, title, voting_end_time]


def save_data():
    create_table()
    asyncio.run(get_data())

