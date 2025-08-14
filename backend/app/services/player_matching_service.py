"""
Player Matching Service for Fantasy XI Wizard
Matches user-input player names to database players using fuzzy matching
"""

from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from difflib import SequenceMatcher
import re

class PlayerMatchingService:
    def __init__(self, db: Session):
        self.db = db

    async def match_player_names(self, player_names: List[str]) -> List[Dict[str, Any]]:
        """Match a list of player names to database players"""
        from app.db.models import Player, Team
        
        # Get all players from database
        players = self.db.query(Player).join(Team).all()
        
        matched_players = []
        
        for input_name in player_names:
            if not input_name.strip():
                continue
                
            best_match = self._find_best_match(input_name.strip(), players)
            if best_match:
                matched_players.append(self._format_player_data(best_match))
        
        return matched_players

    def _find_best_match(self, input_name: str, players: List) -> Optional[Any]:
        """Find the best matching player for an input name"""
        best_score = 0
        best_match = None
        
        # Normalize input name
        normalized_input = self._normalize_name(input_name)
        
        for player in players:
            # Try different name combinations
            name_variants = [
                player.web_name,
                f"{player.first_name} {player.second_name}",
                player.second_name,  # Last name only
                player.first_name,   # First name only
            ]
            
            for variant in name_variants:
                if variant:
                    normalized_variant = self._normalize_name(variant)
                    score = self._calculate_similarity(normalized_input, normalized_variant)
                    
                    if score > best_score and score > 0.6:  # Minimum similarity threshold
                        best_score = score
                        best_match = player
        
        return best_match

    def _normalize_name(self, name: str) -> str:
        """Normalize a name for comparison"""
        # Remove special characters, convert to lowercase
        normalized = re.sub(r'[^\w\s]', '', name.lower())
        # Remove extra whitespace
        normalized = ' '.join(normalized.split())
        return normalized

    def _calculate_similarity(self, name1: str, name2: str) -> float:
        """Calculate similarity between two names"""
        # Use SequenceMatcher for fuzzy matching
        return SequenceMatcher(None, name1, name2).ratio()

    def _format_player_data(self, player) -> Dict[str, Any]:
        """Format player data for transfer analysis"""
        return {
            'player_id': player.id,
            'player_name': f"{player.first_name} {player.second_name}",
            'web_name': player.web_name,
            'position': self._get_position_name(player.element_type),
            'team': player.team.name if player.team else 'Unknown',
            'price': player.now_cost / 10 if player.now_cost else 0,
            'total_points': player.total_points or 0,
            'form': float(player.form) if player.form else 0.0,
            'points_per_game': float(player.points_per_game) if player.points_per_game else 0.0,
            'selected_by_percent': float(player.selected_by_percent) if player.selected_by_percent else 0.0
        }

    def _get_position_name(self, element_type: int) -> str:
        """Convert element type to position name"""
        positions = {1: 'GK', 2: 'DEF', 3: 'MID', 4: 'FWD'}
        return positions.get(element_type, 'Unknown')
