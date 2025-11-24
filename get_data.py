from data.config import NETWORKS
from sql import save_to_db, create_table, check_dublicates, set_option
from _wallet import address_to_address
from dateutil import parser
from itertools import chain
from namada_provider import NamadaProvider

import aiohttp
import asyncio
import time
import logging


logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)


async def get_proposals(session, network):
    # Check if network is Namada
    if network.get('provider') == 'namada':
        return await get_namada_proposals(session, network)
    
    # Get the gov module prefix (e.g., 'atomone' for AtomOne, default 'cosmos')
    gov_prefix = network.get('gov_prefix', 'cosmos')
    
    # Support both single lcd_api and multiple lcd_endpoints
    endpoints = network.get('lcd_endpoints', [network.get('lcd_api')]) if network.get('lcd_api') else network.get('lcd_endpoints', [])
    
    if not endpoints:
        logging.error(f"No LCD endpoints configured for {network['name']}")
        return []
    
    last_error = None
    
    # Try each endpoint until one succeeds
    for endpoint in endpoints:
        # Try v1beta1 first (works for most chains including AtomOne)
        try:
            url = f"{endpoint}/{gov_prefix}/gov/v1beta1/proposals?proposal_status=2&pagination.limit=100"
            print(url)
            async with session.get(url) as resp:
                resp_json = await resp.json()
                props = [prop for prop in resp_json.get('proposals', []) if prop['status'] == 'PROPOSAL_STATUS_VOTING_PERIOD']
                return [parse_proposal(network, prop, api_version='v1beta1') for prop in props]
        except Exception as e:
            last_error = e
            logging.warning(f"v1beta1 API failed for {network['name']} on {endpoint}: {e}")
        
        # Fallback to v1 if v1beta1 fails for this endpoint
        try:
            url = f"{endpoint}/{gov_prefix}/gov/v1/proposals?proposal_status=2&pagination.limit=100"
            async with session.get(url) as resp:
                if resp.status == 200:
                    resp_json = await resp.json()
                    props = [prop for prop in resp_json.get('proposals', []) if prop['status'] == 'PROPOSAL_STATUS_VOTING_PERIOD']
                    return [parse_proposal(network, prop, api_version='v1') for prop in props]
        except Exception as e:
            last_error = e
            logging.warning(f"v1 API failed for {network['name']} on {endpoint}: {e}")
    
    # All endpoints failed
    logging.error(f"All endpoints failed for {network['name']}. Last error: {last_error}")
    return []


async def get_namada_proposals(session, network):
    """
    Get proposals for Namada via custom provider
    """
    try:
        provider = NamadaProvider(network)
        proposals = await provider.get_proposals_with_votes(session)
        
        # Convert to format expected by the rest of the code
        # proposals are in format [network, id, title, end_time, voted]
        result = []
        for prop in proposals:
            # prop = [network, id, title, end_time, voted]
            # We need format [network, id, title, end_time]
            # Vote status will be checked later in get_vote
            result.append(prop[:4])  # Take first 4 elements
        
        return result
    except Exception as e:
        logging.error(f"Error getting Namada proposals for {network['name']}: {e}")
        return []


async def get_vote(session, proposal):
    network = [network for network in NETWORKS if network['name'] == proposal[0]][0]
    
    # For Namada use separate vote checking logic
    if network.get('provider') == 'namada':
        try:
            provider = NamadaProvider(network)
            has_voted = await provider.check_validator_voted(session, proposal[1])
            
            if not has_voted:
                proposal.append(False)
                return proposal
            else:
                set_option(network['name'], proposal[1], True)
                return None
        except Exception as e:
            logging.error(f"Error checking Namada vote for proposal {proposal[1]}: {e}")
            proposal.append(False)
            return proposal
    
    # Standard logic for Cosmos SDK networks
    voter = address_to_address(network['validator'], network['prefix'])
    
    # Get the gov module prefix (e.g., 'atomone' for AtomOne, default 'cosmos')
    gov_prefix = network.get('gov_prefix', 'cosmos')
    
    # Support both single lcd_api and multiple lcd_endpoints
    endpoints = network.get('lcd_endpoints', [network.get('lcd_api')]) if network.get('lcd_api') else network.get('lcd_endpoints', [])
    
    # Try each endpoint until one succeeds
    for endpoint in endpoints:
        try:
            url = f"{endpoint}/{gov_prefix}/gov/v1beta1/proposals/{proposal[1]}/votes/{voter}"
            async with session.get(url) as resp:
                resp_json = await resp.json()
                print(resp_json)
                if 'code' in list(resp_json.keys()):
                    proposal.append(False)
                    return proposal
                else:
                    set_option(network['name'], proposal[1], True)
                    return None
        except Exception as e:
            logging.warning(f"Vote check failed on {endpoint}: {e}")
            continue
    
    # If all endpoints failed, assume not voted
    proposal.append(False)
    return proposal


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
        # print([(p) for p in proposals if p and not check_dublicates(p[0], p[1])])
        logging.info("Data saved in a database")


def parse_proposal(network, proposal: dict, api_version='v1beta1'):
    """
    Parse proposal with support for both v1beta1 and v1 API
    
    v1beta1: uses content.title
    v1: uses title directly (or metadata, or messages[0])
    """
    network_name = network['name']
    
    # Parse ID
    if 'id' in proposal.keys():
        _id = int(proposal['id'])
    else:
        _id = int(proposal.get('proposal_id', proposal.get('id', 0)))
    
    # Parse title depending on API version
    title = None
    
    if api_version == 'v1':
        # For v1 API (AtomOne and modern SDK)
        # Try direct title first
        title = proposal.get('title')
        
        # If no title, try metadata
        if not title and 'metadata' in proposal:
            title = proposal.get('metadata', {}).get('title')
        
        # If no metadata, try summary (sometimes used as description)
        if not title:
            title = proposal.get('summary', '')[:100]  # Limit length
        
        # If nothing found, try messages (legacy content may be in messages)
        if not title and 'messages' in proposal and len(proposal['messages']) > 0:
            first_msg = proposal['messages'][0]
            if 'content' in first_msg:
                title = first_msg['content'].get('title', '')
    else:
        # For v1beta1 API (legacy networks and AtomOne)
        try:
            title = proposal['content']['title']
        except (KeyError, TypeError):
            # Fallback: try to extract from content type (for system proposals like MsgUpdateParams)
            if 'content' in proposal and '@type' in proposal['content']:
                msg_type = proposal['content']['@type']
                # Extract readable name from type (e.g., /atomone.gov.v1.MsgUpdateParams -> Update Gov Params)
                if '.' in msg_type:
                    type_parts = msg_type.split('.')[-1].replace('Msg', '').replace('Update', 'Update ')
                    title = f"{type_parts}"
                else:
                    title = msg_type
            else:
                # Last resort
                title = proposal.get('title', '')
    
    # If still no title found, use default
    if not title:
        logging.warning(f"Could not parse title for proposal {_id} in {network_name}, using default")
        title = 'Proposal (title unavailable)'
    
    # Parse voting end time
    voting_end_time = int(parser.parse(proposal['voting_end_time']).timestamp())
    
    return [network_name, _id, title, voting_end_time]


async def save_data():
    create_table()
    await get_data()


asyncio.run(save_data())

