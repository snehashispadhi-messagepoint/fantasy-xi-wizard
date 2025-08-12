"""
Historical Data-Aware AI Service for Fantasy XI Wizard
Provides intelligent recommendations using historical data for early season predictions
and progressively integrates current season data as it becomes available
"""

import os
import json
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime, date
from sqlalchemy.orm import Session
from sqlalchemy import text

# Import OpenAI client
try:
    from openai import AsyncOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("⚠️ OpenAI package not installed. Install with: pip install openai")

class HistoricalAIService:
    """AI Service with historical data awareness and gameweek-based logic"""
    
    def __init__(self, db: Session = None):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.model = "gpt-4o-mini"
        self.db = db

        # Initialize OpenAI client if available and configured
        if OPENAI_AVAILABLE and self.openai_api_key:
            self.client = AsyncOpenAI(api_key=self.openai_api_key)
            self.use_llm = True
        else:
            self.client = None
            self.use_llm = False
            print("⚠️ OpenAI not configured, using enhanced mock responses")

    async def get_season_config(self) -> Dict[str, Any]:
        """Get current season configuration and AI settings"""
        if not self.db:
            return {
                "season": "2025-26",
                "current_gameweek": 1,
                "use_historical_mode": True,
                "historical_cutoff_gw": 5,
                "ai_weights": {"historical": 0.7, "current": 0.3, "fixtures": 0.1, "team_changes": 0.1}
            }

        try:
            result = self.db.execute(text("""
                SELECT season, current_gameweek, use_historical_mode, 
                       historical_cutoff_gw, ai_weights
                FROM season_config 
                WHERE is_current = TRUE
                LIMIT 1
            """))
            
            row = result.fetchone()
            if row:
                return {
                    "season": row[0],
                    "current_gameweek": row[1],
                    "use_historical_mode": row[2],
                    "historical_cutoff_gw": row[3],
                    "ai_weights": row[4] if row[4] else {"historical": 0.7, "current": 0.3, "fixtures": 0.1, "team_changes": 0.1}
                }
            else:
                # Default config
                return {
                    "season": "2025-26",
                    "current_gameweek": 1,
                    "use_historical_mode": True,
                    "historical_cutoff_gw": 5,
                    "ai_weights": {"historical": 0.7, "current": 0.3, "fixtures": 0.1, "team_changes": 0.1}
                }
        except Exception as e:
            print(f"Error fetching season config: {e}")
            return {
                "season": "2025-26",
                "current_gameweek": 1,
                "use_historical_mode": True,
                "historical_cutoff_gw": 5,
                "ai_weights": {"historical": 0.7, "current": 0.3, "fixtures": 0.1, "team_changes": 0.1}
            }

    async def _fetch_historical_player_data(self, seasons: List[str] = None) -> List[Dict[str, Any]]:
        """Fetch historical player performance data with current team validation"""
        if not self.db:
            return []

        if seasons is None:
            seasons = ['2024-25', '2023-24']  # Default to last 2 seasons

        try:
            # Build query for multiple seasons with team change detection
            season_placeholders = ', '.join([f"'{season}'" for season in seasons])

            result = self.db.execute(text(f"""
                SELECT
                    h.player_id,
                    h.season,
                    h.total_points,
                    h.goals_scored,
                    h.assists,
                    h.clean_sheets,
                    h.minutes,
                    h.points_per_game,
                    h.price_start,
                    h.price_end,
                    h.selected_by_percent_avg,
                    p.web_name,
                    p.first_name,
                    p.second_name,
                    p.element_type,
                    p.now_cost,
                    p.status,
                    p.news,
                    t.name as team_name,
                    t.short_name as team_short,
                    -- Check if player is still active and available
                    CASE
                        WHEN p.status = 'a' THEN true
                        ELSE false
                    END as is_available,
                    -- Check for recent team changes
                    CASE
                        WHEN EXISTS (
                            SELECT 1 FROM team_changes tc
                            WHERE tc.player_id = p.id
                            AND tc.season = '2025-26'
                        ) THEN true
                        ELSE false
                    END as has_team_change
                FROM historical_player_stats h
                JOIN players p ON h.player_id = p.id
                JOIN teams t ON p.team_id = t.id
                WHERE h.season IN ({season_placeholders})
                AND h.total_points > 20
                AND p.status = 'a'  -- Only available players
                ORDER BY h.season DESC, h.total_points DESC
            """))

            historical_data = []
            for row in result:
                position_map = {1: 'GK', 2: 'DEF', 3: 'MID', 4: 'FWD'}
                position = position_map.get(row[14], 'Unknown')

                # Add availability and team change flags
                player_data = {
                    "player_id": row[0],
                    "season": row[1],
                    "total_points": row[2],
                    "goals_scored": row[3],
                    "assists": row[4],
                    "clean_sheets": row[5],
                    "minutes": row[6],
                    "points_per_game": row[7],
                    "price_start": row[8],
                    "price_end": row[9],
                    "selected_by_percent_avg": row[10],
                    "web_name": row[11],
                    "name": f"{row[12]} {row[13]}",
                    "position": position,
                    "element_type": row[14],
                    "current_price": row[15] / 10.0,
                    "status": row[16],
                    "news": row[17] or "",
                    "team": row[18],
                    "team_short": row[19],
                    "is_available": row[20],
                    "has_team_change": row[21],
                    # Add risk assessment based on availability and changes
                    "risk_level": self._assess_player_risk(row[16], row[17], row[21])
                }

                historical_data.append(player_data)

            return historical_data
        except Exception as e:
            print(f"Error fetching historical player data: {e}")
            return []

    def _assess_player_risk(self, status: str, news: str, has_team_change: bool) -> str:
        """Assess player risk level based on status, news, and team changes"""
        if status != 'a':
            return "high"  # Not available

        if has_team_change:
            return "medium"  # New team, adaptation period

        if news and any(keyword in news.lower() for keyword in ['injury', 'doubt', 'suspended', 'banned']):
            return "high"  # Injury or disciplinary issues

        if news and any(keyword in news.lower() for keyword in ['back', 'fit', 'training']):
            return "low"  # Positive news

        return "low"  # Default low risk

    async def _fetch_current_season_data(self) -> List[Dict[str, Any]]:
        """Fetch current season player data (will be minimal for early gameweeks)"""
        if not self.db:
            return []

        try:
            # Import models dynamically to avoid circular imports
            from sqlalchemy import text

            result = self.db.execute(text("""
                SELECT
                    p.id, p.first_name, p.second_name, p.web_name,
                    p.element_type, p.now_cost, p.total_points, p.form,
                    p.goals_scored, p.assists, p.clean_sheets, p.minutes,
                    p.selected_by_percent, p.points_per_game, p.status, p.news,
                    t.name as team_name
                FROM players p
                JOIN teams t ON p.team_id = t.id
                ORDER BY p.total_points DESC
            """))

            players_data = []
            for row in result:
            
                position_map = {1: 'GK', 2: 'DEF', 3: 'MID', 4: 'FWD'}
                position = position_map.get(row[4], 'Unknown')
                price = row[5] / 10.0 if row[5] else 0.0

                players_data.append({
                    "id": row[0],
                    "name": f"{row[1]} {row[2]}",
                    "web_name": row[3],
                    "team": row[16],
                    "position": position,
                    "element_type": row[4],
                    "price": price,
                    "total_points": row[6] or 0,
                    "form": row[7] or 0.0,
                    "goals_scored": row[8] or 0,
                    "assists": row[9] or 0,
                    "clean_sheets": row[10] or 0,
                    "minutes": row[11] or 0,
                    "selected_by_percent": row[12] or 0.0,
                    "points_per_game": row[13] or 0.0,
                    "status": row[14],
                    "news": row[15]
                })

            return players_data
        except Exception as e:
            print(f"Error fetching current season data: {e}")
            return []

    def _determine_ai_mode(self, config: Dict[str, Any]) -> str:
        """Determine whether to use historical or current season mode"""
        current_gw = config.get("current_gameweek", 1)
        cutoff_gw = config.get("historical_cutoff_gw", 5)
        use_historical = config.get("use_historical_mode", True)
        
        if use_historical and current_gw <= cutoff_gw:
            return "historical"
        else:
            return "hybrid"

    def _calculate_data_weights(self, config: Dict[str, Any]) -> Dict[str, float]:
        """Calculate data source weights based on current gameweek"""
        current_gw = config.get("current_gameweek", 1)
        cutoff_gw = config.get("historical_cutoff_gw", 5)
        
        if current_gw <= cutoff_gw:
            # Pre-season mode: Heavy historical weighting
            return {
                "historical_primary": 0.70,  # 2024-25 season
                "historical_secondary": 0.20,  # 2023-24 season  
                "current_season": 0.05,  # Minimal current data
                "fixtures": 0.03,
                "team_changes": 0.02
            }
        else:
            # In-season mode: Progressive current season integration
            current_weight = min(0.6, 0.1 + (current_gw - cutoff_gw) * 0.05)
            historical_weight = max(0.2, 0.7 - (current_gw - cutoff_gw) * 0.05)
            
            return {
                "current_season": current_weight,
                "historical_primary": historical_weight,
                "historical_secondary": 0.1,
                "fixtures": 0.05,
                "team_changes": 0.05
            }

    async def _get_top_historical_performers(self, historical_data: List[Dict], position: str = None, limit: int = 10) -> List[Dict]:
        """Get top performers from historical data"""
        filtered_data = historical_data
        
        if position:
            filtered_data = [p for p in historical_data if p.get("position") == position]
        
        # Group by player and get their best season
        player_best = {}
        for player in filtered_data:
            player_id = player["player_id"]
            if player_id not in player_best or player["total_points"] > player_best[player_id]["total_points"]:
                player_best[player_id] = player
        
        # Sort by total points and return top performers
        top_performers = sorted(player_best.values(), key=lambda x: x["total_points"], reverse=True)
        return top_performers[:limit]

    async def analyze_player_query_historical(
        self,
        query: str,
        context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Analyze natural language queries using historical data awareness"""
        
        # Get season configuration
        config = await self.get_season_config()
        ai_mode = self._determine_ai_mode(config)
        weights = self._calculate_data_weights(config)
        
        # Fetch appropriate data based on mode
        if ai_mode == "historical":
            historical_data = await self._fetch_historical_player_data(['2024-25', '2023-24'])
            current_data = await self._fetch_current_season_data()
        else:
            historical_data = await self._fetch_historical_player_data(['2024-25'])
            current_data = await self._fetch_current_season_data()

        if self.use_llm and self.client:
            return await self._generate_historical_llm_response(
                query, context, historical_data, current_data, config, weights
            )
        else:
            return await self._generate_historical_mock_response(
                query, context, historical_data, current_data, config, weights
            )

    async def _generate_historical_llm_response(
        self,
        query: str,
        context: Optional[Dict],
        historical_data: List[Dict],
        current_data: List[Dict],
        config: Dict[str, Any],
        weights: Dict[str, float]
    ) -> Dict[str, Any]:
        """Generate LLM response using historical data awareness"""

        try:
            current_gw = config.get("current_gameweek", 1)
            ai_mode = self._determine_ai_mode(config)

            # Prepare data for LLM based on mode
            if ai_mode == "historical":
                # Pre-season mode: Focus on historical performance
                top_performers_2024 = await self._get_top_historical_performers(
                    [p for p in historical_data if p["season"] == "2024-25"], limit=15
                )
                top_performers_2023 = await self._get_top_historical_performers(
                    [p for p in historical_data if p["season"] == "2023-24"], limit=10
                )

                # Filter out unavailable players and assess risks
                available_performers_2024 = [p for p in top_performers_2024 if p.get('is_available', True)]
                available_performers_2023 = [p for p in top_performers_2023 if p.get('is_available', True)]

                prompt = f"""
You are an expert Fantasy Premier League (FPL) analyst. The 2025-26 season starts in 3 days (Gameweek {current_gw}).

IMPORTANT: Base recommendations on historical data while considering current player availability and team changes.

AVAILABLE HISTORICAL PERFORMERS (Primary Source - {weights['historical_primary']*100:.0f}% weight):
2024-25 Season Top Available Players:
{self._format_historical_players_with_risk(available_performers_2024[:10])}

2023-24 Season Context ({weights['historical_secondary']*100:.0f}% weight):
{self._format_historical_players_with_risk(available_performers_2023[:5])}

CURRENT SEASON STATUS:
- Gameweek: {current_gw} (Pre-season mode)
- Current season stats: All players start at 0 points
- Prices: Updated for 2025-26 season
- Player availability: Only available players included
- Team changes: Some players have moved clubs

USER QUERY: "{query}"

ANALYSIS APPROACH:
1. Use 2024-25 performance as primary indicator ({weights['historical_primary']*100:.0f}% weight)
2. Consider 2023-24 for consistency patterns ({weights['historical_secondary']*100:.0f}% weight)
3. Factor in current team, price changes, and availability
4. Account for team changes and adaptation periods
5. Prioritize low-risk players for early season stability

IMPORTANT CONSIDERATIONS:
- Only recommend AVAILABLE players (status = available)
- Consider team changes may affect early season performance
- Factor in any injury news or fitness concerns
- Prioritize proven performers who are still at strong clubs

Provide specific player recommendations based on historical performance while considering current availability and team status.

Respond in JSON format:
{{
    "query_type": "historical_analysis",
    "response": "Your detailed analysis and recommendations",
    "confidence": 0.8,
    "key_recommendations": ["Player 1 reasoning", "Player 2 reasoning"],
    "supporting_data": {{
        "top_historical_performers": ["Player names"],
        "analysis_mode": "pre_season_historical_with_availability",
        "data_sources": "2024-25 available players (70%), 2023-24 context (20%), current status (10%)"
    }},
    "ai_reasoning": "Brief explanation of recommendation logic considering availability and team changes"
}}
"""
            else:
                # Hybrid mode: Blend current and historical
                current_top = sorted(current_data, key=lambda x: x.get("total_points", 0), reverse=True)[:10]
                historical_top = await self._get_top_historical_performers(historical_data, limit=10)

                prompt = f"""
You are an expert Fantasy Premier League (FPL) analyst. We're in Gameweek {current_gw} of the 2025-26 season.

CURRENT SEASON DATA (Primary Source - {weights['current_season']*100:.0f}% weight):
{self._format_current_players(current_top)}

HISTORICAL CONTEXT ({weights['historical_primary']*100:.0f}% weight):
2024-25 Season Performance:
{self._format_historical_players(historical_top)}

USER QUERY: "{query}"

ANALYSIS APPROACH:
1. Prioritize current season form and performance ({weights['current_season']*100:.0f}% weight)
2. Use historical data for context and consistency ({weights['historical_primary']*100:.0f}% weight)
3. Identify trends and momentum
4. Consider fixture difficulty

Blend current performance with historical context to provide informed recommendations.

Respond in JSON format with detailed analysis.
"""

            # Call OpenAI API
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert FPL analyst providing data-driven advice using historical performance data."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1200
            )

            llm_response = response.choices[0].message.content

            try:
                recommendation = json.loads(llm_response)
                recommendation["data_source"] = "historical_aware_ai"
                recommendation["llm_model"] = self.model
                recommendation["ai_mode"] = ai_mode
                recommendation["gameweek"] = current_gw
                recommendation["data_weights"] = weights
                recommendation["generated_at"] = datetime.now().isoformat()
                return recommendation

            except json.JSONDecodeError:
                # Fallback response if JSON parsing fails
                return {
                    "query_type": "historical_analysis",
                    "response": llm_response,
                    "confidence": 0.8,
                    "supporting_data": {
                        "ai_mode": ai_mode,
                        "gameweek": current_gw,
                        "note": "LLM response in text format"
                    },
                    "data_source": "historical_aware_ai",
                    "llm_model": self.model,
                    "data_weights": weights
                }

        except Exception as e:
            print(f"Error calling OpenAI API for historical query: {e}")
            return await self._generate_historical_mock_response(
                query, context, historical_data, current_data, config, weights
            )

    def _format_historical_players(self, players: List[Dict]) -> str:
        """Format historical player data for LLM prompt"""
        formatted = []
        for player in players[:8]:  # Limit to avoid token overflow
            formatted.append(
                f"- {player['web_name']} ({player['position']}, {player['team']}): "
                f"{player['total_points']} pts, {player['goals_scored']}G {player['assists']}A, "
                f"£{player['current_price']:.1f}m"
            )
        return "\n".join(formatted)

    def _format_historical_players_with_risk(self, players: List[Dict]) -> str:
        """Format historical player data with risk assessment for LLM prompt"""
        formatted = []
        for player in players[:8]:  # Limit to avoid token overflow
            risk_indicator = ""
            if player.get('has_team_change'):
                risk_indicator = " [NEW TEAM]"
            elif player.get('risk_level') == 'medium':
                risk_indicator = " [CAUTION]"
            elif player.get('risk_level') == 'high':
                risk_indicator = " [HIGH RISK]"

            news_info = ""
            if player.get('news'):
                news_info = f" - {player['news'][:50]}..."

            formatted.append(
                f"- {player['web_name']} ({player['position']}, {player['team']}){risk_indicator}: "
                f"{player['total_points']} pts, {player['goals_scored']}G {player['assists']}A, "
                f"£{player['current_price']:.1f}m{news_info}"
            )
        return "\n".join(formatted)

    def _format_current_players(self, players: List[Dict]) -> str:
        """Format current season player data for LLM prompt"""
        formatted = []
        for player in players[:8]:
            formatted.append(
                f"- {player['web_name']} ({player['position']}, {player['team']}): "
                f"{player['total_points']} pts, {player['goals_scored']}G {player['assists']}A, "
                f"Form: {player['form']:.1f}, £{player['price']:.1f}m"
            )
        return "\n".join(formatted)

    async def _generate_historical_mock_response(
        self,
        query: str,
        context: Optional[Dict],
        historical_data: List[Dict],
        current_data: List[Dict],
        config: Dict[str, Any],
        weights: Dict[str, float]
    ) -> Dict[str, Any]:
        """Generate enhanced mock response using historical data when LLM unavailable"""

        current_gw = config.get("current_gameweek", 1)
        ai_mode = self._determine_ai_mode(config)

        # Get top historical performers (only available players)
        available_historical_data = [p for p in historical_data if p.get('is_available', True)]
        top_performers = await self._get_top_historical_performers(available_historical_data, limit=5)

        # Analyze query type
        query_lower = query.lower()

        if any(word in query_lower for word in ['11 players', 'starting team', 'team selection', 'formation', 'squad']):
            # Team selection recommendation
            return await self._generate_team_selection_response(
                query, historical_data, current_data, config, weights
            )
        elif any(word in query_lower for word in ['captain', 'captaincy', 'armband']):
            # Captain recommendation
            captain_candidates = [p for p in top_performers if p['position'] in ['MID', 'FWD']][:3]

            # Add availability context
            availability_note = ""
            if captain_candidates[0].get('has_team_change'):
                availability_note = f" Note: {captain_candidates[0]['web_name']} has moved to {captain_candidates[0]['team']} this season, so monitor early form."
            elif captain_candidates[0].get('news'):
                availability_note = f" Latest: {captain_candidates[0]['news']}"

            response = f"Based on historical data from 2024-25, I recommend **{captain_candidates[0]['web_name']}** as captain for GW{current_gw}. "
            response += f"He scored {captain_candidates[0]['total_points']} points last season with {captain_candidates[0]['goals_scored']} goals. "
            response += f"Alternative options include {captain_candidates[1]['web_name']} ({captain_candidates[1]['total_points']} pts) and {captain_candidates[2]['web_name']} ({captain_candidates[2]['total_points']} pts)."
            response += availability_note

            return {
                "query_type": "captain_recommendation",
                "response": response,
                "confidence": 0.85,
                "key_recommendations": [
                    f"{captain_candidates[0]['web_name']}: Top scorer last season",
                    f"{captain_candidates[1]['web_name']}: Consistent performer",
                    f"{captain_candidates[2]['web_name']}: Value option"
                ],
                "supporting_data": {
                    "captain_options": [
                        {
                            "name": p['web_name'],
                            "position": p['position'],
                            "team": p['team'],
                            "last_season_points": p['total_points'],
                            "price": p['current_price']
                        } for p in captain_candidates
                    ],
                    "analysis_mode": ai_mode,
                    "data_source": "2024-25 historical performance"
                },
                "data_source": "historical_aware_mock",
                "ai_mode": ai_mode,
                "gameweek": current_gw,
                "data_weights": weights,
                "ai_reasoning": f"Recommendations based on {weights['historical_primary']*100:.0f}% historical data weighting for early season predictions"
            }

        elif any(word in query_lower for word in ['transfer', 'buy', 'sell', 'replace']):
            # Transfer recommendation
            value_picks = sorted(top_performers, key=lambda x: x['total_points'] / x['current_price'], reverse=True)[:3]

            response = f"For transfers, consider these value picks based on 2024-25 performance: "
            response += f"**{value_picks[0]['web_name']}** (£{value_picks[0]['current_price']:.1f}m, {value_picks[0]['total_points']} pts), "
            response += f"**{value_picks[1]['web_name']}** (£{value_picks[1]['current_price']:.1f}m, {value_picks[1]['total_points']} pts), "
            response += f"and **{value_picks[2]['web_name']}** (£{value_picks[2]['current_price']:.1f}m, {value_picks[2]['total_points']} pts). "
            response += "These players offer excellent points-per-million based on last season's data."

            return {
                "query_type": "transfer_recommendation",
                "response": response,
                "confidence": 0.8,
                "key_recommendations": [f"{p['web_name']}: {p['total_points']/p['current_price']:.1f} pts/£m" for p in value_picks],
                "supporting_data": {
                    "transfer_targets": [
                        {
                            "name": p['web_name'],
                            "position": p['position'],
                            "team": p['team'],
                            "price": p['current_price'],
                            "last_season_points": p['total_points'],
                            "value_score": p['total_points'] / p['current_price']
                        } for p in value_picks
                    ],
                    "analysis_mode": ai_mode
                },
                "data_source": "historical_aware_mock",
                "ai_mode": ai_mode,
                "gameweek": current_gw,
                "data_weights": weights
            }

        else:
            # General recommendation
            response = f"Based on 2024-25 historical data, here are my top recommendations for GW{current_gw}: "
            response += f"**{top_performers[0]['web_name']}** ({top_performers[0]['position']}) was the standout performer with {top_performers[0]['total_points']} points. "
            response += f"**{top_performers[1]['web_name']}** and **{top_performers[2]['web_name']}** are also excellent choices. "
            response += f"Since we're in the early gameweeks, I'm using {weights['historical_primary']*100:.0f}% historical data weighting for these predictions."

            return {
                "query_type": "general_recommendation",
                "response": response,
                "confidence": 0.8,
                "key_recommendations": [f"{p['web_name']}: {p['total_points']} points in 2024-25" for p in top_performers[:3]],
                "supporting_data": {
                    "top_players": [
                        {
                            "name": p['web_name'],
                            "position": p['position'],
                            "team": p['team'],
                            "last_season_points": p['total_points'],
                            "price": p['current_price']
                        } for p in top_performers[:5]
                    ],
                    "analysis_mode": ai_mode,
                    "historical_seasons": ["2024-25", "2023-24"]
                },
                "data_source": "historical_aware_mock",
                "ai_mode": ai_mode,
                "gameweek": current_gw,
                "data_weights": weights,
                "ai_reasoning": "Early season predictions based primarily on historical performance data"
            }

    async def _generate_team_selection_response(
        self,
        query: str,
        historical_data: List[Dict],
        current_data: List[Dict],
        config: Dict[str, Any],
        weights: Dict[str, float]
    ) -> Dict[str, Any]:
        """Generate detailed team selection with 11 players"""

        current_gw = config.get("current_gameweek", 1)
        ai_mode = self._determine_ai_mode(config)

        # Define formation (default 3-5-2)
        formation = {"GK": 1, "DEF": 3, "MID": 5, "FWD": 2}
        if "3-4-3" in query.lower():
            formation = {"GK": 1, "DEF": 3, "MID": 4, "FWD": 3}
        elif "4-5-1" in query.lower():
            formation = {"GK": 1, "DEF": 4, "MID": 5, "FWD": 1}
        elif "4-4-2" in query.lower():
            formation = {"GK": 1, "DEF": 4, "MID": 4, "FWD": 2}

        # Group players by position
        positions = {"GK": [], "DEF": [], "MID": [], "FWD": []}
        for player in historical_data:
            pos = player['position']
            if pos in positions:
                positions[pos].append(player)

        # Sort by total points and select top players for each position
        selected_team = []
        total_cost = 0
        position_details = {}

        for pos, count in formation.items():
            # Sort by total points descending
            sorted_players = sorted(positions[pos], key=lambda x: x['total_points'], reverse=True)

            selected_players = []
            for i, player in enumerate(sorted_players[:count]):
                price = player['current_price']
                total_cost += price

                player_info = {
                    "name": player['web_name'],
                    "team": player['team'],
                    "price": price,
                    "last_season_points": player['total_points'],
                    "goals": player['goals_scored'],
                    "assists": player['assists'],
                    "position": player['position']
                }

                selected_players.append(player_info)
                selected_team.append(player)

            position_details[pos.lower()] = selected_players

        # Create detailed response
        formation_str = f"{formation['DEF']}-{formation['MID']}-{formation['FWD']}"

        response = f"Here's your optimal 11-player team for the next 5 gameweeks in {formation_str} formation, based on 2024-25 historical performance:\n\n"

        # Add position breakdown
        pos_names = {"GK": "GOALKEEPER", "DEF": "DEFENDERS", "MID": "MIDFIELDERS", "FWD": "FORWARDS"}
        for pos, players in position_details.items():
            response += f"**{pos_names[pos.upper()]}:**\n"
            for player in players:
                response += f"• {player['name']} ({player['team']}) - £{player['price']:.1f}m\n"
                response += f"  2024-25: {player['last_season_points']} pts, {player['goals']}G {player['assists']}A\n"
            response += "\n"

        response += f"**TEAM COST:** £{total_cost:.1f}m\n"
        response += f"**REMAINING BUDGET:** £{100 - total_cost:.1f}m\n\n"

        # Captain recommendation
        captain = max(selected_team, key=lambda x: x['total_points'])
        response += f"**CAPTAIN RECOMMENDATION:** {captain['web_name']} ({captain['total_points']} pts in 2024-25)\n\n"

        response += f"This team is based on {weights['historical_primary']*100:.0f}% historical data weighting for early season reliability."

        return {
            "query_type": "team_selection",
            "response": response,
            "confidence": 0.9,
            "key_recommendations": [
                f"Captain: {captain['web_name']} ({captain['total_points']} pts)",
                f"Best value: {min(selected_team, key=lambda x: x['current_price'])['web_name']} (£{min(selected_team, key=lambda x: x['current_price'])['current_price']:.1f}m)",
                f"Formation: {formation_str} with £{100-total_cost:.1f}m remaining"
            ],
            "supporting_data": {
                "team_selection": position_details,
                "formation": formation_str,
                "total_cost": total_cost,
                "remaining_budget": 100 - total_cost,
                "captain_recommendation": {
                    "name": captain['web_name'],
                    "team": captain['team'],
                    "last_season_points": captain['total_points'],
                    "price": captain['current_price']
                },
                "analysis_mode": ai_mode,
                "data_source": "2024-25 historical performance"
            },
            "data_source": "historical_aware_mock",
            "ai_mode": ai_mode,
            "gameweek": current_gw,
            "data_weights": weights,
            "ai_reasoning": f"Team selection based on {weights['historical_primary']*100:.0f}% historical data for proven early season performance"
        }
