"""
Namada Provider для получения информации о пропоузалах
Реализация основана на tenderduty: https://github.com/Firstset/tenderduty
"""

import aiohttp
import logging
from typing import List, Dict, Any, Optional
from dateutil import parser

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)


class NamadaProvider:
    """
    Провайдер для работы с Namada blockchain через HTTP API индексера.
    Namada не использует стандартный модуль Cosmos SDK x/gov.
    """

    def __init__(self, network: Dict[str, Any]):
        """
        Инициализация провайдера Namada
        
        Args:
            network: Словарь с конфигурацией сети
                - name: Имя сети
                - indexers: Список URL индексеров Namada
                - validator_address: Адрес валидатора в формате tnam...
                - explorer: URL эксплорера для формирования ссылок
        """
        self.network_name = network['name']
        self.indexers = network.get('indexers', [])
        self.validator_address = network.get('validator_address', '')
        self.explorer = network.get('explorer', '')

        if not self.indexers:
            raise ValueError(f"Namada network {self.network_name} requires 'indexers' list")
        if not self.validator_address:
            raise ValueError(f"Namada network {self.network_name} requires 'validator_address'")

    async def get_voting_period_proposals(self, session: aiohttp.ClientSession) -> List[Dict[str, Any]]:
        """
        Получить список пропоузалов в стадии голосования
        
        Returns:
            Список пропоузалов в унифицированном формате
        """
        last_error = None
        
        # Try each indexer in sequence
        for indexer_url in self.indexers:
            try:
                url = f"{indexer_url}/api/v1/gov/proposal?status=votingPeriod"
                logging.info(f"Querying Namada indexer: {url}")
                
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                    if resp.status != 200:
                        last_error = f"HTTP {resp.status}"
                        continue
                    
                    data = await resp.json()
                    proposals = []
                    
                    # Process each proposal from response
                    for namada_proposal in data.get('results', []):
                        try:
                            proposal = self._convert_namada_proposal(namada_proposal)
                            if proposal:
                                proposals.append(proposal)
                        except Exception as e:
                            logging.warning(f"Failed to convert proposal {namada_proposal.get('id')}: {e}")
                            continue
                    
                    if proposals:
                        logging.info(f"Found {len(proposals)} voting period proposals from {indexer_url}")
                        return proposals
                        
            except aiohttp.ClientError as e:
                last_error = str(e)
                logging.warning(f"Failed to query indexer {indexer_url}: {e}")
                continue
            except Exception as e:
                last_error = str(e)
                logging.error(f"Unexpected error with indexer {indexer_url}: {e}")
                continue
        
        logging.error(f"All indexers failed for {self.network_name}. Last error: {last_error}")
        return []

    def _convert_namada_proposal(self, namada_proposal: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Convert Namada proposal to unified format
        
        Args:
            namada_proposal: Proposal from Namada API
            
        Returns:
            Unified dictionary with proposal data or None on error
        """
        try:
            # Parse ID (in Namada it's a string, convert to int)
            proposal_id = int(namada_proposal['id'])
            
            # Parse voting end time
            end_time_str = namada_proposal['endTime']
            voting_end_time = int(end_time_str)  # Unix timestamp in seconds
            
            # Form title (in Namada can be type or content)
            title = namada_proposal.get('content', namada_proposal.get('type', 'Namada Proposal'))
            
            return {
                'network': self.network_name,
                'id': proposal_id,
                'title': title,
                'voting_end_time': voting_end_time,
                'status': namada_proposal.get('status', 'voting'),
            }
            
        except (KeyError, ValueError, TypeError) as e:
            logging.error(f"Error converting Namada proposal: {e}")
            return None

    async def check_validator_voted(
        self, 
        session: aiohttp.ClientSession, 
        proposal_id: int
    ) -> bool:
        """
        Проверить, проголосовал ли валидатор за данный пропоузал
        
        Args:
            session: aiohttp session
            proposal_id: Proposal ID
            
        Returns:
            True if validator has voted, False otherwise
        """
        # Try each indexer
        for indexer_url in self.indexers:
            try:
                url = f"{indexer_url}/api/v1/gov/voter/{self.validator_address}/votes"
                
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                    if resp.status != 200:
                        continue
                    
                    votes = await resp.json()
                    
                    # Check if there's a vote for this proposal
                    for vote in votes:
                        vote_proposal_id = vote.get('proposalId')
                        
                        # Handle as float (from JSON) and as string
                        if vote_proposal_id is not None:
                            try:
                                if int(float(vote_proposal_id)) == proposal_id:
                                    logging.info(
                                        f"Validator {self.validator_address} has voted on proposal {proposal_id}"
                                    )
                                    return True
                            except (ValueError, TypeError):
                                continue
                    
                    # If we got here - no vote found
                    return False
                    
            except Exception as e:
                logging.warning(f"Error checking vote on {indexer_url}: {e}")
                continue
        
        # If all indexers failed, assume not voted
        logging.warning(f"Could not verify vote status for proposal {proposal_id}")
        return False

    async def get_proposals_with_votes(
        self, 
        session: aiohttp.ClientSession
    ) -> List[List[Any]]:
        """
        Get proposals and check validator voting status
        
        Returns:
            List in format [network_name, proposal_id, title, voting_end_time, voted]
        """
        proposals = await self.get_voting_period_proposals(session)
        result = []
        
        for proposal in proposals:
            has_voted = await self.check_validator_voted(session, proposal['id'])
            
            # Form result in format compatible with main code
            result.append([
                proposal['network'],
                proposal['id'],
                proposal['title'],
                proposal['voting_end_time'],
                has_voted  # True if voted
            ])
        
        return result
