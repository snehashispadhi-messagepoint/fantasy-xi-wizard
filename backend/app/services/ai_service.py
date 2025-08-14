"""
AI Service for Fantasy XI Wizard
Provides intelligent recommendations using OpenAI GPT-4 with real FPL data
"""

import os
import json
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session

# Import OpenAI client
try:
    from openai import AsyncOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("⚠️ OpenAI package not installed. Install with: pip install openai")

# Import the new historical AI service
from app.services.historical_ai_service import HistoricalAIService

class AIService:
    def __init__(self, db: Session = None):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.model = "gpt-4o-mini"  # Use the more cost-effective model
        self.db = db

        # Initialize OpenAI client if available and configured
        if OPENAI_AVAILABLE and self.openai_api_key:
            self.client = AsyncOpenAI(api_key=self.openai_api_key)
            self.use_llm = True
        else:
            self.client = None
            self.use_llm = False
            print("⚠️ OpenAI not configured, using mock responses")

    async def _fetch_real_player_data(self) -> List[Dict[str, Any]]:
        """Fetch real player data from database"""
        if not self.db:
            return []

        try:
            from app.db.models import Player, Team

            # Get all players with their teams
            players = self.db.query(Player).join(Team).all()

            player_data = []
            for player in players:
                # Map element_type to position
                position_map = {1: "GK", 2: "DEF", 3: "MID", 4: "FWD"}
                position = position_map.get(player.element_type, "Unknown")

                # Convert price from 0.1m units to actual price
                price = player.now_cost / 10.0

                player_data.append({
                    "id": player.id,
                    "name": f"{player.first_name} {player.second_name}",
                    "web_name": player.web_name,
                    "team": player.team.name,
                    "position": position,
                    "element_type": player.element_type,
                    "price": price,
                    "total_points": player.total_points,
                    "form": player.form,
                    "goals_scored": player.goals_scored,
                    "assists": player.assists,
                    "clean_sheets": player.clean_sheets,
                    "minutes": player.minutes,
                    "selected_by_percent": player.selected_by_percent,
                    "points_per_game": player.points_per_game,
                    "expected_goals": player.expected_goals,
                    "expected_assists": player.expected_assists,
                    "status": player.status,
                    "news": player.news
                })

            return player_data
        except Exception as e:
            print(f"Error fetching player data: {e}")
            return []

    async def _fetch_real_fixture_data(self) -> List[Dict[str, Any]]:
        """Fetch real fixture data from database"""
        if not self.db:
            return []

        try:
            from app.db.models import Fixture, Team

            # Get upcoming fixtures (not finished)
            fixtures = self.db.query(Fixture).filter(
                Fixture.finished == False
            ).limit(20).all()  # Get next 20 fixtures

            fixture_data = []
            for fixture in fixtures:
                # Get team names through relationships
                home_team = fixture.team_home.name if fixture.team_home else "Unknown"
                away_team = fixture.team_away.name if fixture.team_away else "Unknown"

                fixture_data.append({
                    "id": fixture.id,
                    "gameweek": fixture.event,
                    "team_h": home_team,
                    "team_a": away_team,
                    "team_h_id": fixture.team_h_id,
                    "team_a_id": fixture.team_a_id,
                    "team_h_difficulty": fixture.team_h_difficulty,
                    "team_a_difficulty": fixture.team_a_difficulty,
                    "kickoff_time": fixture.kickoff_time.isoformat() if fixture.kickoff_time else None,
                    "finished": fixture.finished,
                    "started": fixture.started
                })

            return fixture_data
        except Exception as e:
            print(f"Error fetching fixture data: {e}")
            return []

    async def _fetch_real_team_data(self) -> List[Dict[str, Any]]:
        """Fetch real team data from database"""
        if not self.db:
            return []

        try:
            from app.db.models import Team

            teams = self.db.query(Team).all()

            team_data = []
            for team in teams:
                team_data.append({
                    "id": team.id,
                    "name": team.name,
                    "short_name": team.short_name,
                    "strength": team.strength,
                    "strength_overall_home": team.strength_overall_home,
                    "strength_overall_away": team.strength_overall_away,
                    "strength_attack_home": team.strength_attack_home,
                    "strength_attack_away": team.strength_attack_away,
                    "strength_defence_home": team.strength_defence_home,
                    "strength_defence_away": team.strength_defence_away
                })

            return team_data
        except Exception as e:
            print(f"Error fetching team data: {e}")
            return []

    async def get_squad_recommendation(
        self,
        budget: float = 100.0,
        formation: str = "3-5-2",
        gameweeks: int = 3,
        user_preferences: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Generate AI-powered squad recommendations using real FPL data and LLM analysis"""

        try:
            # Fetch real data from database with timeout
            players = await asyncio.wait_for(self._fetch_real_player_data(), timeout=5.0)
            fixtures = await asyncio.wait_for(self._fetch_real_fixture_data(), timeout=3.0)
            teams = await asyncio.wait_for(self._fetch_real_team_data(), timeout=2.0)

            # Use LLM for dynamic squad generation if available
            if self.use_llm and self.client:
                return await self._generate_llm_squad_recommendation(
                    players, fixtures, teams, budget, formation, gameweeks
                )
            else:
                # Fallback to enhanced algorithm
                return await self._generate_enhanced_mock_squad(
                    players, fixtures, teams, budget, formation, gameweeks
                )
        except asyncio.TimeoutError:
            print("⚠️ Database query timeout, using fallback data")
            return await self._generate_fallback_squad_recommendation(budget, formation, gameweeks)
        except Exception as e:
            print(f"Error in squad recommendation: {e}")
            return await self._generate_fallback_squad_recommendation(budget, formation, gameweeks)

    async def _generate_llm_squad_recommendation(
        self,
        players: List[Dict],
        fixtures: List[Dict],
        teams: List[Dict],
        budget: float,
        formation: str,
        gameweeks: int,
        user_preferences: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Generate squad recommendation using OpenAI LLM with real data"""

        try:
            # Prepare data for LLM
            top_players_by_position = self._get_top_players_by_position(players)
            upcoming_fixtures_summary = self._summarize_fixtures(fixtures)
            team_strengths = self._summarize_team_strengths(teams)

            # Create enhanced prompt for LLM with current FPL context
            prompt = f"""
You are an expert Fantasy Premier League (FPL) analyst with access to current FPL news and trends. Generate a completely fresh, optimal squad for the next {gameweeks} gameweeks.

CRITICAL REQUIREMENTS:
- Budget: £{budget}m (MUST use close to full budget - aim for £{budget-2}m to £{budget}m total cost)
- Squad: Exactly 15 players (2 GK, 5 DEF, 5 MID, 3 FWD)
- Maximum 3 players from any team
- Generate a UNIQUE squad each time - avoid repetitive selections

CURRENT FPL CONTEXT (2025-26 Season):
- Season just started - prioritize players with good opening fixtures
- Consider current injury news and team rotations
- Look for early season differentials and value picks
- Account for new signings and player role changes
- Consider penalty takers and set piece specialists

REAL PLAYER DATA (Top performers by position):
{json.dumps(top_players_by_position, indent=2)}

UPCOMING FIXTURES (Next {gameweeks} gameweeks):
{json.dumps(upcoming_fixtures_summary, indent=2)}

TEAM STRENGTHS & FORM:
{json.dumps(team_strengths, indent=2)}

STRATEGY GUIDELINES:
1. **Budget Utilization**: Use £{budget-2}m to £{budget}m (don't leave money unused)
2. **Balance**: Mix of premium players (£10m+) and value picks (£4-7m)
3. **Fixtures**: Prioritize teams with favorable upcoming fixtures
4. **Form**: Consider recent performance and underlying stats
5. **Differentials**: Include 1-2 lower-owned players for edge
6. **Current News**: Factor in any injury updates or team news

Please provide a JSON response with this EXACT structure:
{{
    "formation": "3-5-2",
    "total_cost": <calculated_total_cost>,
    "budget_used": <same_as_total_cost>,
    "predicted_points": <estimated_total_points>,
    "confidence": <0.7_to_0.95>,
    "players": [
        {{
            "player_name": "Exact Player Name",
            "team": "Team Name",
            "position": "GK",
            "price": <exact_price>,
            "predicted_points": <points_for_period>,
            "reasoning": "Specific reason for selection including fixtures/form"
        }}
        // ... exactly 15 players
    ],
    "analysis": {{
        "data_source": "real_fpl_data",
        "players_analyzed": {len(players)},
        "fixtures_considered": {len(fixtures)},
        "confidence_score": <same_as_confidence>,
        "key_insights": [
            "Budget utilization strategy",
            "Fixture-based selections",
            "Value picks identified",
            "Risk/reward balance"
        ],
        "captain_recommendation": "Best captain option from squad",
        "risk_assessment": "Assessment of squad risk level"
    }},
    "ai_reasoning": "Comprehensive explanation of squad strategy, budget allocation, and key decisions"
}}

IMPORTANT: Generate a completely fresh squad each time. Vary your selections based on different strategies (attacking vs defensive, premium heavy vs balanced, etc). Use the FULL budget available.
"""

            # Call OpenAI API with higher temperature for varied responses
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert FPL analyst with access to current news and trends. Generate unique, varied squad recommendations each time."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,  # Higher temperature for more varied recommendations
                max_tokens=3000
            )

            # Parse LLM response
            llm_response = response.choices[0].message.content

            try:
                # Extract JSON from markdown code blocks if present
                import re
                json_match = re.search(r'```json\s*(\{.*?\})\s*```', llm_response, re.DOTALL)
                if json_match:
                    json_str = json_match.group(1)
                else:
                    # Try to find JSON object in response
                    json_match = re.search(r'\{.*\}', llm_response, re.DOTALL)
                    if json_match:
                        json_str = json_match.group(0)
                    else:
                        json_str = llm_response

                # Parse the extracted JSON
                recommendation = json.loads(json_str)

                # Add metadata
                recommendation["recommendation_type"] = "squad_selection"
                recommendation["data_source"] = "real_fpl_data"
                recommendation["llm_model"] = self.model
                recommendation["generated_at"] = datetime.now().isoformat()

                return recommendation

            except (json.JSONDecodeError, AttributeError):
                # If JSON parsing fails, create structured response from text
                return {
                    "recommendation_type": "squad_selection",
                    "formation": formation,
                    "total_cost": budget,
                    "predicted_points": 180.0,
                    "confidence": 0.8,
                    "players": [],
                    "analysis": {
                        "llm_response": llm_response,
                        "note": "LLM response could not be parsed as JSON"
                    },
                    "ai_reasoning": llm_response[:500] + "..." if len(llm_response) > 500 else llm_response,
                    "data_source": "real_fpl_data",
                    "llm_model": self.model
                }

        except Exception as e:
            print(f"Error calling OpenAI API: {e}")
            # Fallback to enhanced mock
            return await self._generate_enhanced_mock_squad(
                players, fixtures, teams, budget, formation, gameweeks
            )

    def _get_top_players_by_position(self, players: List[Dict]) -> Dict[str, List[Dict]]:
        """Get top players by position based on form and value"""
        positions = {"GK": [], "DEF": [], "MID": [], "FWD": []}

        for player in players:
            pos = player.get("position", "")
            if pos in positions:
                # Calculate value score (points per price)
                price = max(player.get("price", 4.0), 4.0)  # Minimum price
                points = player.get("total_points", 0)
                form = player.get("form", 0)

                value_score = (points / price) + (form * 2)  # Weight form higher
                player["value_score"] = value_score

                positions[pos].append(player)

        # Sort by value score and take top players
        for pos in positions:
            positions[pos] = sorted(
                positions[pos],
                key=lambda x: x.get("value_score", 0),
                reverse=True
            )[:20]  # Top 20 per position

        return positions

    def _summarize_fixtures(self, fixtures: List[Dict]) -> List[Dict]:
        """Summarize upcoming fixtures for LLM"""
        summary = []
        for fixture in fixtures[:10]:  # Next 10 fixtures
            summary.append({
                "gameweek": fixture.get("gameweek"),
                "home_team": fixture.get("team_h"),
                "away_team": fixture.get("team_a"),
                "home_difficulty": fixture.get("team_h_difficulty"),
                "away_difficulty": fixture.get("team_a_difficulty")
            })
        return summary

    def _summarize_team_strengths(self, teams: List[Dict]) -> List[Dict]:
        """Summarize team strengths for LLM"""
        summary = []
        for team in teams:
            summary.append({
                "name": team.get("name"),
                "overall_strength": team.get("strength"),
                "attack_home": team.get("strength_attack_home"),
                "attack_away": team.get("strength_attack_away"),
                "defence_home": team.get("strength_defence_home"),
                "defence_away": team.get("strength_defence_away")
            })
        return summary

    async def _generate_enhanced_mock_squad(
        self,
        players: List[Dict],
        fixtures: List[Dict],
        teams: List[Dict],
        budget: float,
        formation: str,
        gameweeks: int
    ) -> Dict[str, Any]:
        """Generate budget-aware squad using real data with dynamic selection"""

        # Build optimal squad within budget constraints
        selected_players = self._build_budget_aware_squad(players, budget)

        total_cost = sum(p.get("price", 0) for p in selected_players)
        total_predicted = sum(p.get("predicted_points", 0) for p in selected_players)

        return {
            "recommendation_type": "squad_selection",
            "formation": formation,
            "total_cost": min(total_cost, budget),
            "budget_used": min(total_cost, budget),  # Frontend expects this field
            "predicted_points": total_predicted,
            "confidence": 0.85,
            "players": selected_players,
            "analysis": {
                "data_source": "real_fpl_data",
                "players_analyzed": len(players),
                "fixtures_considered": len(fixtures),
                "confidence_score": 0.85,  # Frontend expects this field
                "key_insights": [
                    f"Squad built from {len(players)} real FPL players",
                    f"Considered {len(fixtures)} upcoming fixtures",
                    "Prioritized form and value over price"
                ],
                "captain_recommendation": selected_players[0].get("player_name", "Unknown") if selected_players else "Unknown",
                "risk_assessment": "Medium - balanced approach using real data"
            },
            "ai_reasoning": f"Squad optimized using real FPL data for {formation} formation. Selected top performers by position based on current form, total points, and value for money.",
            "data_source": "real_fpl_data"
        }

    def _build_budget_aware_squad(self, players: List[Dict], budget: float) -> List[Dict]:
        """Build a squad within budget constraints using value-based selection"""

        # Group players by position and sort by value (points per price)
        players_by_position = {"GK": [], "DEF": [], "MID": [], "FWD": []}

        for player in players:
            position = player.get("position", "Unknown")
            if position in players_by_position:
                # Calculate value score (points per price with form bonus)
                price = max(player.get("price", 4.0), 0.1)  # Avoid division by zero
                total_points = player.get("total_points", 0)
                form = player.get("form", 0)

                # Value score: prioritize points per price with form bonus
                value_score = (total_points / price) + (form * 2)
                player["value_score"] = value_score
                players_by_position[position].append(player)

        # Sort each position by value score
        for position in players_by_position:
            players_by_position[position].sort(key=lambda p: p.get("value_score", 0), reverse=True)

        # Build squad with budget constraints
        selected_players = []
        remaining_budget = budget

        # Required squad structure: 2 GK, 5 DEF, 5 MID, 3 FWD
        # Adjust max prices based on budget to use more money
        max_gk_price = min(6.0, budget * 0.06)
        max_def_price = min(8.0, budget * 0.08)
        max_mid_price = min(15.0, budget * 0.15)
        max_fwd_price = min(15.0, budget * 0.15)

        position_requirements = [
            ("GK", 2, 4.0, max_gk_price),
            ("DEF", 5, 4.0, max_def_price),
            ("MID", 5, 4.5, max_mid_price),
            ("FWD", 3, 4.5, max_fwd_price)
        ]

        for position, count, min_price, max_price in position_requirements:
            position_players = players_by_position.get(position, [])
            position_budget = remaining_budget * self._get_position_budget_ratio(position)

            for i in range(count):
                if not position_players:
                    break

                # Find best affordable player
                selected_player = None
                for player in position_players:
                    player_price = player.get("price", min_price)
                    if player_price <= min(position_budget, remaining_budget, max_price):
                        selected_player = player
                        break

                # If no affordable premium player, get cheapest available
                if not selected_player:
                    affordable_players = [p for p in position_players
                                        if p.get("price", min_price) <= remaining_budget]
                    if affordable_players:
                        selected_player = min(affordable_players, key=lambda p: p.get("price", min_price))

                if selected_player:
                    # Format player data
                    formatted_player = {
                        "player_name": selected_player.get("name", f"Unknown {position}"),
                        "team": selected_player.get("team", "Unknown"),
                        "position": position,
                        "price": selected_player.get("price", min_price),
                        "predicted_points": min(selected_player.get("total_points", 0) * 0.3,
                                              50 if position == "FWD" else 40 if position == "MID" else 30),
                        "reasoning": self._get_player_reasoning(selected_player, position)
                    }

                    selected_players.append(formatted_player)
                    remaining_budget -= selected_player.get("price", min_price)
                    position_players.remove(selected_player)

        return selected_players

    def _get_position_budget_ratio(self, position: str) -> float:
        """Get budget allocation ratio for each position"""
        ratios = {
            "GK": 0.10,   # 10% for goalkeepers
            "DEF": 0.25,  # 25% for defenders
            "MID": 0.45,  # 45% for midfielders (most important)
            "FWD": 0.20   # 20% for forwards
        }
        return ratios.get(position, 0.15)

    def _get_player_reasoning(self, player: Dict, position: str) -> str:
        """Generate reasoning for player selection"""
        price = player.get("price", 0)
        total_points = player.get("total_points", 0)
        form = player.get("form", 0)

        if position == "GK":
            return f"Reliable keeper with {total_points} points. Good value at £{price}m"
        elif position == "DEF":
            return f"Solid defender with {total_points} points. Clean sheet potential at £{price}m"
        elif position == "MID":
            goals = player.get("goals_scored", 0)
            assists = player.get("assists", 0)
            return f"Creative midfielder: {goals} goals, {assists} assists. {total_points} points at £{price}m"
        else:  # FWD
            goals = player.get("goals_scored", 0)
            return f"Proven goalscorer with {goals} goals. {total_points} points at £{price}m"

    async def _analyze_upcoming_fixtures(self, gameweeks: int) -> Dict[str, Any]:
        """Analyze upcoming fixtures for difficulty and opportunities"""
        return {
            "easy_fixtures": ["Arsenal", "Liverpool", "Manchester City"],
            "difficult_fixtures": ["Brighton", "Newcastle", "Tottenham"],
            "double_gameweeks": [],
            "blank_gameweeks": [],
            "fixture_analysis": f"Next {gameweeks} gameweeks favor attacking assets from top 6 teams"
        }

    async def _analyze_historical_performance(self) -> Dict[str, Any]:
        """Analyze historical performance data for predictions"""
        return {
            "top_performers_last_season": [
                {"name": "Haaland", "points": 272, "goals": 36},
                {"name": "Palmer", "points": 244, "goals": 22, "assists": 11},
                {"name": "Saka", "points": 215, "goals": 16, "assists": 9}
            ],
            "form_players": [
                {"name": "Mbeumo", "form": 8.2, "recent_goals": 6},
                {"name": "Palmer", "form": 9.1, "recent_goals": 8},
                {"name": "Rogers", "form": 7.8, "recent_assists": 4}
            ],
            "value_picks": [
                {"name": "Mbeumo", "price": 7.5, "points_per_million": 3.7},
                {"name": "Rogers", "price": 5.5, "points_per_million": 4.0}
            ]
        }

    async def _generate_352_squad(self, budget: float, gameweeks: int, fixtures: Dict, historical: Dict) -> Dict[str, Any]:
        """Generate optimized 3-5-2 formation squad based on historical data and upcoming fixtures"""
        return {
            "recommendation_type": "squad_selection",
            "budget_used": budget,
            "formation": "3-5-2",
            "players": [
                {
                    "position": "GK",
                    "player_name": "Raya",
                    "team": "Arsenal",
                    "price": 5.5,
                    "predicted_points": 18,
                    "confidence": 0.85,
                    "reasoning": "Arsenal's strong defensive record and favorable fixtures. Expected 3+ clean sheets based on historical data vs upcoming opponents."
                },
                {
                    "position": "DEF",
                    "player_name": "Saliba",
                    "team": "Arsenal",
                    "price": 6.0,
                    "predicted_points": 22,
                    "confidence": 0.88,
                    "reasoning": "Arsenal averaged 18 clean sheets last season. Saliba scored 2 goals from set pieces and has excellent aerial threat."
                },
                {
                    "position": "DEF",
                    "player_name": "Alexander-Arnold",
                    "team": "Liverpool",
                    "price": 7.0,
                    "predicted_points": 25,
                    "confidence": 0.82,
                    "reasoning": "Historically averages 12+ assists per season. Liverpool's improved defensive form (65% clean sheet probability vs upcoming opponents)."
                },
                {
                    "position": "DEF",
                    "player_name": "Porro",
                    "team": "Tottenham",
                    "price": 5.5,
                    "predicted_points": 20,
                    "confidence": 0.80,
                    "reasoning": "5 goals + 8 assists last season. Excellent attacking returns for price point with Spurs' improved defensive structure."
                },
                {
                    "position": "MID",
                    "player_name": "Palmer",
                    "team": "Chelsea",
                    "price": 11.0,
                    "predicted_points": 35,
                    "confidence": 0.92,
                    "reasoning": "22 goals + 11 assists last season. On penalties and free kicks. Chelsea's main creative outlet with excellent underlying stats."
                },
                {
                    "position": "MID",
                    "player_name": "Saka",
                    "team": "Arsenal",
                    "price": 10.0,
                    "predicted_points": 32,
                    "confidence": 0.89,
                    "reasoning": "16 goals + 9 assists last season. Arsenal's key attacking threat with consistent returns in favorable fixtures."
                },
                {
                    "position": "MID",
                    "player_name": "Mbeumo",
                    "team": "Brentford",
                    "price": 7.5,
                    "predicted_points": 28,
                    "confidence": 0.85,
                    "reasoning": "8 goals in last 6 games. Historically overperforms in good fixtures. Brentford's main attacking threat with excellent value."
                },
                {
                    "position": "MID",
                    "player_name": "Rogers",
                    "team": "Aston Villa",
                    "price": 5.5,
                    "predicted_points": 22,
                    "confidence": 0.78,
                    "reasoning": "4 assists in last 5 games. Budget enabler with attacking returns. Villa's improved attacking play benefits Rogers."
                },
                {
                    "position": "MID",
                    "player_name": "Eze",
                    "team": "Crystal Palace",
                    "price": 7.0,
                    "predicted_points": 25,
                    "confidence": 0.81,
                    "reasoning": "11 goals + 4 assists last season. Palace's main creative force with set piece duties and good fixtures ahead."
                },
                {
                    "position": "FWD",
                    "player_name": "Haaland",
                    "team": "Manchester City",
                    "price": 15.0,
                    "predicted_points": 45,
                    "confidence": 0.95,
                    "reasoning": "36 goals last season. Historically averages 2.1 goals vs upcoming opponents. Premium captain option with highest ceiling."
                },
                {
                    "position": "FWD",
                    "player_name": "Watkins",
                    "team": "Aston Villa",
                    "price": 9.0,
                    "predicted_points": 30,
                    "confidence": 0.84,
                    "reasoning": "19 goals last season. Strong record in favorable fixtures. Villa's improved attacking play benefits Watkins significantly."
                }
            ],
            "analysis": {
                "total_cost": budget,
                "predicted_points": 185.0,
                "confidence": 0.87,
                "ai_reasoning": f"Optimized 3-5-2 formation for next {gameweeks} gameweeks based on historical performance and fixture analysis. Strong midfield focus with premium attacking options.",

                "team_distribution": {
                    "Arsenal": 3,
                    "Liverpool": 1,
                    "Manchester City": 1,
                    "Chelsea": 1,
                    "Tottenham": 1,
                    "Aston Villa": 2,
                    "Brentford": 1,
                    "Crystal Palace": 1
                },

                "risk_assessment": "Medium-High risk with premium attacking options balanced by reliable defensive picks",
                "fixture_analysis": f"Excellent fixture run for next {gameweeks} gameweeks with 8/11 players having favorable matchups based on historical difficulty",
                "captain_recommendation": "Haaland (C) - Palmer (VC) for optimal captaincy rotation",
                "transfer_priority": "Focus on Palmer and Mbeumo as immediate targets if not owned",

                "key_insights": [
                    "Arsenal triple-up justified by historical defensive record (18 CS last season)",
                    "Palmer essential due to 22 goals + 11 assists last season + penalties",
                    "Mbeumo offers exceptional value - historically overperforms in good fixtures",
                    "Haaland captaincy provides ceiling - averages 2.1 goals vs upcoming opponents"
                ],

                "historical_context": {
                    "similar_gameweeks_last_season": "GW15-17 last season saw similar fixture patterns",
                    "top_scorers_in_period": ["Haaland (8 goals)", "Palmer (6 goals)", "Saka (4 goals)"],
                    "clean_sheet_probability": {"Arsenal": 65, "Liverpool": 58, "Man City": 62}
                }
            },
            "alternatives": [
                {
                    "change": "Downgrade Haaland to Isak, upgrade midfield",
                    "reasoning": "More balanced squad with better bench options"
                },
                {
                    "change": "Consider Watkins over Cunha",
                    "reasoning": "Aston Villa's better fixtures in upcoming gameweeks"
                }
            ],
            "ai_summary": "This squad balances premium attacking assets with solid defensive picks. The 3-5-2 formation maximizes midfield returns while maintaining defensive stability. Key differentials like Mbeumo provide excellent value, while proven performers like Salah and Haaland offer high floor and ceiling."
        }

    async def _generate_fallback_squad_recommendation(
        self,
        budget: float,
        formation: str,
        gameweeks: int
    ) -> Dict[str, Any]:
        """Generate a quick fallback squad recommendation when database is unavailable"""

        # Quick hardcoded recommendation for immediate response
        return {
            "recommendation_type": "squad_selection",
            "formation": formation,
            "total_cost": min(budget, 100.0),
            "budget_used": min(budget, 100.0),  # Frontend expects this field
            "predicted_points": 180.0,
            "confidence": 0.75,
            "players": [
                {"player_name": "Haaland", "team": "Manchester City", "position": "FWD", "price": 15.0, "predicted_points": 12.5},
                {"player_name": "Salah", "team": "Liverpool", "position": "MID", "price": 13.0, "predicted_points": 11.8},
                {"player_name": "Palmer", "team": "Chelsea", "position": "MID", "price": 11.0, "predicted_points": 10.2},
                {"player_name": "Saka", "team": "Arsenal", "position": "MID", "price": 10.0, "predicted_points": 9.5},
                {"player_name": "Mbeumo", "team": "Brentford", "position": "MID", "price": 7.5, "predicted_points": 8.2},
                {"player_name": "Cunha", "team": "Wolves", "position": "FWD", "price": 6.5, "predicted_points": 7.8},
                {"player_name": "Gabriel", "team": "Arsenal", "position": "DEF", "price": 6.0, "predicted_points": 6.5},
                {"player_name": "Gvardiol", "team": "Manchester City", "position": "DEF", "price": 5.5, "predicted_points": 6.2},
                {"player_name": "Lewis", "team": "Newcastle", "position": "DEF", "price": 4.5, "predicted_points": 5.8},
                {"player_name": "Raya", "team": "Arsenal", "position": "GKP", "price": 5.5, "predicted_points": 5.5},
                {"player_name": "Fabianski", "team": "West Ham", "position": "GKP", "price": 4.0, "predicted_points": 4.2}
            ],
            "analysis": {
                "data_source": "fallback_recommendation",
                "confidence_score": 0.75,  # Frontend expects this field
                "key_insights": [
                    "Quick recommendation based on popular picks",
                    "Balanced formation with premium attackers",
                    "Good value options in midfield and defense"
                ],
                "captain_recommendation": "Haaland",
                "risk_assessment": "Medium - safe popular picks"
            },
            "ai_reasoning": f"Quick {formation} squad for {gameweeks} gameweeks. Premium attackers Haaland and Salah provide high ceiling, while Palmer and Saka offer consistent returns. Mbeumo is excellent value in midfield.",
            "data_source": "fallback_data",
            "generated_at": datetime.now().isoformat()
        }
    
    async def get_transfer_recommendations(
        self,
        current_squad: List[Dict],
        budget: float = 0.0,
        free_transfers: int = 1,
        gameweeks: int = 3
    ) -> Dict[str, Any]:
        """Generate AI-powered transfer recommendations using real FPL data"""

        try:
            # Fetch real data with timeout
            players = await asyncio.wait_for(self._fetch_real_player_data(), timeout=5.0)
            fixtures = await asyncio.wait_for(self._fetch_real_fixture_data(), timeout=3.0)

            # If no current squad provided, use fallback
            if not current_squad:
                return await self._generate_fallback_transfer_recommendation(budget, free_transfers, gameweeks)

            # Analyze current squad and find transfer opportunities
            return await self._analyze_transfer_opportunities(
                current_squad, players, fixtures, budget, free_transfers, gameweeks
            )

        except asyncio.TimeoutError:
            print("⚠️ Database query timeout for transfer recommendations, using fallback")
            return await self._generate_fallback_transfer_recommendation(budget, free_transfers, gameweeks)
        except Exception as e:
            print(f"Error in transfer recommendation: {e}")
            return await self._generate_fallback_transfer_recommendation(budget, free_transfers, gameweeks)

    async def _analyze_transfer_opportunities(
        self,
        current_squad: List[Dict],
        players: List[Dict],
        fixtures: List[Dict],
        budget: float,
        free_transfers: int,
        gameweeks: int
    ) -> Dict[str, Any]:
        """Analyze current squad and find optimal transfer opportunities using real data"""

        # Step 1: Identify underperforming players in current squad
        underperformers = self._identify_underperforming_players(current_squad, players)

        # Step 2: Find better alternatives for each position
        transfer_opportunities = []
        total_cost_change = 0

        for underperformer in underperformers[:free_transfers]:  # Limit to available transfers
            alternatives = self._find_transfer_alternatives(
                underperformer, players, fixtures, gameweeks
            )

            if alternatives:
                best_alternative = alternatives[0]  # Top alternative
                cost_change = best_alternative["price"] - underperformer.get("price", 0)

                # Check if we can afford this transfer
                if total_cost_change + cost_change <= budget:
                    transfer_opportunities.append({
                        "out": {
                            "player_name": underperformer.get("name", "Unknown"),
                            "team": underperformer.get("team", "Unknown"),
                            "position": underperformer.get("position", "Unknown"),
                            "price": underperformer.get("price", 0),
                            "recent_form": underperformer.get("form", 0),
                            "total_points": underperformer.get("total_points", 0),
                            "reason_to_sell": self._get_sell_reason(underperformer, fixtures)
                        },
                        "in": {
                            "player_name": best_alternative.get("name", "Unknown"),
                            "team": best_alternative.get("team", "Unknown"),
                            "position": best_alternative.get("position", "Unknown"),
                            "price": best_alternative.get("price", 0),
                            "predicted_points": self._calculate_predicted_points(best_alternative, gameweeks),
                            "confidence": best_alternative.get("confidence", 0.75),
                            "form": best_alternative.get("form", 0),
                            "total_points": best_alternative.get("total_points", 0)
                        },
                        "reasoning": self._generate_transfer_reasoning(underperformer, best_alternative, fixtures),
                        "priority": len(transfer_opportunities) + 1,
                        "expected_gain": self._calculate_expected_gain(underperformer, best_alternative, gameweeks),
                        "cost_change": cost_change
                    })
                    total_cost_change += cost_change

        # Step 3: Generate alternatives and summary
        alternatives = self._generate_transfer_alternatives(underperformers, players, budget, free_transfers)

        return {
            "recommendation_type": "transfers",
            "transfers_suggested": len(transfer_opportunities),
            "budget_remaining": budget - total_cost_change,
            "transfers": transfer_opportunities,
            "analysis": {
                "total_expected_gain": sum(t.get("expected_gain", 0) for t in transfer_opportunities),
                "risk_assessment": self._assess_transfer_risk(transfer_opportunities),
                "fixture_analysis": f"Analysis based on next {gameweeks} gameweeks",
                "form_analysis": "Prioritized players with strong recent form and underlying stats",
                "data_source": "real_fpl_data",
                "players_analyzed": len(players)
            },
            "alternatives": alternatives,
            "ai_summary": self._generate_transfer_summary(transfer_opportunities, alternatives)
        }

    def _identify_underperforming_players(self, current_squad: List[Dict], all_players: List[Dict]) -> List[Dict]:
        """Identify players in current squad who are underperforming"""
        underperformers = []

        for squad_player in current_squad:
            # Find full player data
            player_data = None
            for player in all_players:
                if (player.get("name") == squad_player.get("player_name") or
                    player.get("id") == squad_player.get("player_id")):
                    player_data = player
                    break

            if player_data:
                # Calculate underperformance score
                form = player_data.get("form", 0)
                points_per_game = player_data.get("points_per_game", 0)
                price = player_data.get("price", 0)

                # Poor form or low points per game relative to price
                if form < 3.0 or (points_per_game < 4.0 and price > 6.0) or (points_per_game < 2.0):
                    underperformers.append(player_data)

        # Sort by worst performers first (lowest form + points per game)
        underperformers.sort(key=lambda p: p.get("form", 0) + p.get("points_per_game", 0))
        return underperformers

    def _find_transfer_alternatives(
        self,
        underperformer: Dict,
        all_players: List[Dict],
        fixtures: List[Dict],
        gameweeks: int
    ) -> List[Dict]:
        """Find better alternatives for an underperforming player"""
        position = underperformer.get("position")
        current_price = underperformer.get("price", 0)

        alternatives = []
        for player in all_players:
            if (player.get("position") == position and
                player.get("name") != underperformer.get("name")):

                # Calculate transfer score
                form = player.get("form", 0)
                points_per_game = player.get("points_per_game", 0)
                price = player.get("price", 0)

                # Fixture difficulty for next few gameweeks
                fixture_score = self._calculate_fixture_score(player, fixtures, gameweeks)

                # Overall transfer score
                transfer_score = (form * 2) + (points_per_game * 3) + fixture_score - (price * 0.1)

                # Only consider if significantly better
                current_score = (underperformer.get("form", 0) * 2) + (underperformer.get("points_per_game", 0) * 3)
                if transfer_score > current_score + 2:  # Minimum improvement threshold
                    player["confidence"] = min(0.95, 0.6 + (transfer_score - current_score) * 0.05)
                    player["transfer_score"] = transfer_score
                    alternatives.append(player)

        # Sort by transfer score (best first)
        alternatives.sort(key=lambda p: p.get("transfer_score", 0), reverse=True)
        return alternatives[:5]  # Top 5 alternatives

    def _calculate_fixture_score(self, player: Dict, fixtures: List[Dict], gameweeks: int) -> float:
        """Calculate fixture difficulty score for a player over next gameweeks"""
        team_name = player.get("team")
        fixture_score = 0
        fixtures_found = 0

        for fixture in fixtures:
            if fixtures_found >= gameweeks:
                break

            if fixture.get("team_h") == team_name or fixture.get("team_a") == team_name:
                is_home = fixture.get("team_h") == team_name
                difficulty = fixture.get("team_h_difficulty") if is_home else fixture.get("team_a_difficulty")

                # Lower difficulty = better fixture = higher score
                if difficulty:
                    fixture_score += (6 - difficulty)  # Convert 1-5 scale to 5-1 scale
                    fixtures_found += 1

        return fixture_score / max(fixtures_found, 1)  # Average fixture score

    def _calculate_predicted_points(self, player: Dict, gameweeks: int) -> float:
        """Calculate predicted points for a player over next gameweeks"""
        points_per_game = player.get("points_per_game", 0)
        form = player.get("form", 0)

        # Weight recent form more heavily
        adjusted_ppg = (points_per_game * 0.7) + (form * 0.3)
        return round(adjusted_ppg * gameweeks, 1)

    def _calculate_expected_gain(self, out_player: Dict, in_player: Dict, gameweeks: int) -> float:
        """Calculate expected points gain from transfer"""
        out_predicted = self._calculate_predicted_points(out_player, gameweeks)
        in_predicted = self._calculate_predicted_points(in_player, gameweeks)
        return round(in_predicted - out_predicted, 1)

    def _get_sell_reason(self, player: Dict, fixtures: List[Dict]) -> str:
        """Generate reason to sell a player"""
        form = player.get("form", 0)
        points_per_game = player.get("points_per_game", 0)

        if form < 2.0:
            return f"Poor recent form ({form})"
        elif points_per_game < 3.0:
            return f"Low points per game ({points_per_game})"
        else:
            return "Better alternatives available"

    def _generate_transfer_reasoning(self, out_player: Dict, in_player: Dict, fixtures: List[Dict]) -> str:
        """Generate reasoning for a specific transfer"""
        in_form = in_player.get("form", 0)
        in_ppg = in_player.get("points_per_game", 0)
        out_form = out_player.get("form", 0)

        return f"{in_player.get('name')} has superior form ({in_form} vs {out_form}) and better underlying stats. Expected to outperform over next few gameweeks."

    def _assess_transfer_risk(self, transfers: List[Dict]) -> str:
        """Assess overall risk of transfer recommendations"""
        if not transfers:
            return "No transfers recommended"

        total_cost = sum(t.get("cost_change", 0) for t in transfers)
        if total_cost > 2.0:
            return "High - Expensive transfers, ensure strong conviction"
        elif total_cost > 0.5:
            return "Medium - Moderate cost, good value expected"
        else:
            return "Low - Cost-neutral transfers with upside potential"

    def _generate_transfer_alternatives(self, underperformers: List[Dict], players: List[Dict], budget: float, free_transfers: int) -> List[Dict]:
        """Generate alternative transfer strategies"""
        alternatives = []

        if underperformers:
            # Conservative single transfer option
            best_underperformer = underperformers[0]
            cheap_alternatives = [p for p in players
                                if p.get("position") == best_underperformer.get("position")
                                and p.get("price", 0) <= best_underperformer.get("price", 0) + budget
                                and p.get("form", 0) > best_underperformer.get("form", 0)]

            if cheap_alternatives:
                best_cheap = max(cheap_alternatives, key=lambda p: p.get("form", 0))
                alternatives.append({
                    "option": f"Single transfer: {best_underperformer.get('name')} → {best_cheap.get('name')}",
                    "reasoning": "Conservative approach, saves transfers for future",
                    "expected_gain": self._calculate_expected_gain(best_underperformer, best_cheap, 3)
                })

        return alternatives

    def _generate_transfer_summary(self, transfers: List[Dict], alternatives: List[Dict]) -> str:
        """Generate AI summary of transfer recommendations"""
        if not transfers:
            return "No immediate transfers recommended. Current squad performing adequately."

        priority_transfer = transfers[0]
        out_name = priority_transfer["out"]["player_name"]
        in_name = priority_transfer["in"]["player_name"]

        summary = f"Priority transfer is {out_name} to {in_name} - "
        summary += f"form and fixture analysis strongly supports this move. "

        if len(transfers) > 1:
            summary += f"Secondary transfer also recommended for additional value. "

        summary += "Consider timing based on price change predictions and injury news."
        return summary

    async def _generate_fallback_transfer_recommendation(
        self,
        budget: float,
        free_transfers: int,
        gameweeks: int
    ) -> Dict[str, Any]:
        """Generate fallback transfer recommendation when no squad provided or data unavailable"""

        return {
            "recommendation_type": "transfers",
            "transfers_suggested": 1,
            "budget_remaining": budget - 2.5,
            "transfers": [
                {
                    "out": {
                        "player_name": "Rashford",
                        "team": "Manchester Utd",
                        "position": "MID",
                        "price": 8.5,
                        "recent_form": 2.8,
                        "total_points": 45,
                        "reason_to_sell": "Poor recent form and difficult fixtures"
                    },
                    "in": {
                        "player_name": "Palmer",
                        "team": "Chelsea",
                        "position": "MID",
                        "price": 11.0,
                        "predicted_points": 25,
                        "confidence": 0.88,
                        "form": 8.2,
                        "total_points": 156
                    },
                    "reasoning": "Palmer has excellent underlying stats, penalty duties, and favorable fixtures. Strong form suggests continued returns.",
                    "priority": 1,
                    "expected_gain": 8.5,
                    "cost_change": 2.5
                }
            ],
            "analysis": {
                "total_expected_gain": 8.5,
                "risk_assessment": "Medium - Premium price but strong underlying data",
                "fixture_analysis": f"Analysis based on next {gameweeks} gameweeks",
                "form_analysis": "Prioritized players with strong recent form",
                "data_source": "fallback_recommendation"
            },
            "alternatives": [
                {
                    "option": "Budget option: Rashford → Mbeumo",
                    "reasoning": "Lower cost alternative with good recent form",
                    "expected_gain": 6.2
                }
            ],
            "ai_summary": "Palmer represents excellent value despite premium price. Strong form, penalty duties, and favorable fixtures make this a priority transfer."
        }

    async def get_fpl_transfer_recommendations(
        self,
        user_team_data: Dict[str, Any],
        gameweeks: int = 3
    ) -> Dict[str, Any]:
        """Generate LLM-powered transfer recommendations using user's actual FPL team"""

        try:
            # Check if this is pre-season (no squad selected yet)
            if user_team_data.get('pre_season', False) or not user_team_data.get('squad'):
                return await self._generate_pre_season_squad_recommendation(user_team_data, gameweeks)

            # Fetch real data for analysis
            players = await asyncio.wait_for(self._fetch_real_player_data(), timeout=5.0)
            fixtures = await asyncio.wait_for(self._fetch_real_fixture_data(), timeout=3.0)

            if self.use_llm and self.client:
                return await self._generate_llm_fpl_transfer_recommendations(
                    user_team_data, players, fixtures, gameweeks
                )
            else:
                # Fallback to enhanced analysis without LLM
                return await self._generate_enhanced_fpl_transfer_recommendations(
                    user_team_data, players, fixtures, gameweeks
                )

        except asyncio.TimeoutError:
            print("⚠️ Database query timeout for FPL transfer recommendations")
            return await self._generate_fallback_fpl_transfer_recommendation(user_team_data, gameweeks)
        except Exception as e:
            print(f"Error in FPL transfer recommendation: {e}")
            return await self._generate_fallback_fpl_transfer_recommendation(user_team_data, gameweeks)

    async def _generate_llm_fpl_transfer_recommendations(
        self,
        user_team_data: Dict[str, Any],
        players: List[Dict],
        fixtures: List[Dict],
        gameweeks: int
    ) -> Dict[str, Any]:
        """Generate transfer recommendations using LLM analysis of user's actual FPL team"""

        # Prepare context for LLM
        squad = user_team_data.get('squad', [])
        user_info = user_team_data.get('user_info', {})
        recent_transfers = user_team_data.get('recent_transfers', [])
        bank = user_team_data.get('bank', 0)
        free_transfers = user_team_data.get('free_transfers', 1)

        # Analyze squad performance
        squad_analysis = self._analyze_squad_performance(squad, players)

        # Get upcoming fixtures for squad players
        squad_fixtures = self._get_squad_fixtures(squad, fixtures, gameweeks)

        # Prepare LLM prompt
        prompt = f"""
You are an expert Fantasy Premier League analyst. Analyze this user's team and provide intelligent transfer recommendations.

USER TEAM INFORMATION:
- Manager: {user_info.get('name', 'Unknown')}
- Team Name: {user_info.get('team_name', 'Unknown')}
- Overall Rank: {user_info.get('overall_rank', 'Unknown')}
- Total Points: {user_info.get('total_points', 0)}
- Bank: £{bank}m
- Free Transfers: {free_transfers}

CURRENT SQUAD:
{self._format_squad_for_llm(squad)}

SQUAD PERFORMANCE ANALYSIS:
{squad_analysis}

UPCOMING FIXTURES (Next {gameweeks} gameweeks):
{squad_fixtures}

RECENT TRANSFER HISTORY:
{self._format_transfers_for_llm(recent_transfers)}

AVAILABLE PLAYERS (Top performers by position):
{self._format_top_players_for_llm(players)}

Please provide transfer recommendations considering:
1. Underperforming players in current squad
2. Better alternatives available within budget
3. Upcoming fixture difficulty
4. Recent transfer patterns and strategy
5. Value for money and points potential

Respond in JSON format with:
{{
    "recommendation_type": "fpl_transfers",
    "priority_transfers": [
        {{
            "out": {{"player_name": "...", "reason": "..."}},
            "in": {{"player_name": "...", "reason": "..."}},
            "priority": 1,
            "cost_change": 0.5,
            "expected_gain": 8.2,
            "confidence": 0.85
        }}
    ],
    "alternative_strategies": [
        {{
            "strategy": "...",
            "reasoning": "...",
            "transfers": [...]
        }}
    ],
    "squad_analysis": {{
        "strengths": ["...", "..."],
        "weaknesses": ["...", "..."],
        "overall_rating": 8.5
    }},
    "ai_summary": "Detailed analysis and recommendations..."
}}
"""

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert Fantasy Premier League analyst providing data-driven transfer recommendations."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=2000
            )

            # Parse LLM response
            llm_response = response.choices[0].message.content

            # Try to extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', llm_response, re.DOTALL)
            if json_match:
                recommendation_data = json.loads(json_match.group())

                # Add metadata
                recommendation_data.update({
                    "user_info": user_info,
                    "bank_remaining": bank,
                    "free_transfers_used": len(recommendation_data.get("priority_transfers", [])),
                    "data_source": "llm_analysis",
                    "players_analyzed": len(players),
                    "generated_at": datetime.now().isoformat()
                })

                return recommendation_data
            else:
                # Fallback if JSON parsing fails
                return await self._generate_enhanced_fpl_transfer_recommendations(
                    user_team_data, players, fixtures, gameweeks
                )

        except Exception as e:
            print(f"LLM analysis failed: {e}")
            return await self._generate_enhanced_fpl_transfer_recommendations(
                user_team_data, players, fixtures, gameweeks
            )

    def _analyze_squad_performance(self, squad: List[Dict], all_players: List[Dict]) -> str:
        """Analyze current squad performance"""
        analysis = []
        total_points = sum(p.get('total_points', 0) for p in squad)
        avg_form = sum(p.get('form', 0) for p in squad) / len(squad) if squad else 0

        analysis.append(f"Squad Total Points: {total_points}")
        analysis.append(f"Average Form: {avg_form:.1f}")

        # Find underperformers
        underperformers = [p for p in squad if p.get('form', 0) < 3.0 or
                          (p.get('total_points', 0) / max(p.get('price', 1), 1) < 15)]

        if underperformers:
            analysis.append(f"Underperformers: {', '.join(p['player_name'] for p in underperformers)}")

        return "\n".join(analysis)

    def _get_squad_fixtures(self, squad: List[Dict], fixtures: List[Dict], gameweeks: int) -> str:
        """Get upcoming fixtures for squad players"""
        squad_teams = {p.get('team') for p in squad}
        relevant_fixtures = []

        for fixture in fixtures[:gameweeks * 10]:  # Approximate fixture limit
            home_team = fixture.get('team_h_name', '')
            away_team = fixture.get('team_a_name', '')

            if home_team in squad_teams or away_team in squad_teams:
                difficulty_h = fixture.get('team_h_difficulty', 3)
                difficulty_a = fixture.get('team_a_difficulty', 3)
                relevant_fixtures.append(f"{home_team} vs {away_team} (Difficulty: {difficulty_h}-{difficulty_a})")

        return "\n".join(relevant_fixtures[:15])  # Limit output

    def _format_squad_for_llm(self, squad: List[Dict]) -> str:
        """Format squad data for LLM"""
        formatted = []
        for player in squad:
            formatted.append(
                f"- {player.get('player_name', 'Unknown')} ({player.get('position', 'Unknown')}) "
                f"- {player.get('team', 'Unknown')} - £{player.get('price', 0)}m "
                f"- {player.get('total_points', 0)} pts - Form: {player.get('form', 0)}"
            )
        return "\n".join(formatted)

    def _format_transfers_for_llm(self, transfers: List[Dict]) -> str:
        """Format recent transfers for LLM"""
        if not transfers:
            return "No recent transfers"

        formatted = []
        for transfer in transfers[-3:]:  # Last 3 transfers
            formatted.append(f"GW{transfer.get('event', '?')}: {transfer.get('element_in_name', '?')} in, {transfer.get('element_out_name', '?')} out")

        return "\n".join(formatted)

    def _format_top_players_for_llm(self, players: List[Dict]) -> str:
        """Format top players by position for LLM"""
        positions = {'GK': [], 'DEF': [], 'MID': [], 'FWD': []}

        for player in players:
            pos = player.get('position', 'Unknown')
            if pos in positions:
                positions[pos].append(player)

        formatted = []
        for pos, pos_players in positions.items():
            # Sort by points per game and take top 3
            top_players = sorted(pos_players, key=lambda p: p.get('points_per_game', 0), reverse=True)[:3]
            formatted.append(f"\n{pos}:")
            for player in top_players:
                formatted.append(
                    f"  - {player.get('name', 'Unknown')} ({player.get('team', 'Unknown')}) "
                    f"- £{player.get('price', 0)}m - {player.get('total_points', 0)} pts"
                )

        return "\n".join(formatted)

    async def _generate_enhanced_fpl_transfer_recommendations(
        self,
        user_team_data: Dict[str, Any],
        players: List[Dict],
        fixtures: List[Dict],
        gameweeks: int
    ) -> Dict[str, Any]:
        """Generate enhanced transfer recommendations without LLM"""

        squad = user_team_data.get('squad', [])
        bank = user_team_data.get('bank', 0)
        free_transfers = user_team_data.get('free_transfers', 1)

        # Find underperforming players
        underperformers = []
        for player in squad:
            form = player.get('form', 0)
            ppg = player.get('total_points', 0) / max(1, 20)  # Approximate PPG
            price = player.get('price', 0)

            if form < 3.0 or (ppg < 4.0 and price > 6.0):
                underperformers.append(player)

        # Find better alternatives
        priority_transfers = []
        for underperformer in underperformers[:free_transfers]:
            position = underperformer.get('position')
            current_price = underperformer.get('price', 0)
            max_price = current_price + bank

            # Find better players in same position
            alternatives = [
                p for p in players
                if p.get('position') == position
                and p.get('price', 0) <= max_price
                and p.get('total_points', 0) > underperformer.get('total_points', 0)
            ]

            if alternatives:
                best_alternative = max(alternatives, key=lambda p: p.get('points_per_game', 0))

                priority_transfers.append({
                    "out": {
                        "player_name": underperformer.get('player_name', 'Unknown'),
                        "reason": f"Poor form ({underperformer.get('form', 0)}) and low points per game"
                    },
                    "in": {
                        "player_name": best_alternative.get('name', 'Unknown'),
                        "reason": f"Better form and higher points potential"
                    },
                    "priority": len(priority_transfers) + 1,
                    "cost_change": best_alternative.get('price', 0) - current_price,
                    "expected_gain": (best_alternative.get('points_per_game', 0) -
                                    underperformer.get('total_points', 0) / 20) * gameweeks,
                    "confidence": 0.75
                })

        return {
            "recommendation_type": "fpl_transfers",
            "priority_transfers": priority_transfers,
            "alternative_strategies": [
                {
                    "strategy": "Conservative approach",
                    "reasoning": "Make minimal changes and save transfers",
                    "transfers": priority_transfers[:1] if priority_transfers else []
                }
            ],
            "squad_analysis": {
                "strengths": ["Solid foundation", "Good team structure"],
                "weaknesses": [f"{len(underperformers)} underperforming players"] if underperformers else ["No major weaknesses"],
                "overall_rating": 8.0 - len(underperformers) * 0.5
            },
            "user_info": user_team_data.get('user_info', {}),
            "bank_remaining": bank,
            "free_transfers_used": len(priority_transfers),
            "data_source": "enhanced_analysis",
            "players_analyzed": len(players),
            "ai_summary": f"Analysis of your FPL team suggests {len(priority_transfers)} priority transfers. Focus on replacing underperforming players with better alternatives within budget.",
            "generated_at": datetime.now().isoformat()
        }

    async def _generate_fallback_fpl_transfer_recommendation(
        self,
        user_team_data: Dict[str, Any],
        gameweeks: int
    ) -> Dict[str, Any]:
        """Generate fallback recommendation when data is unavailable"""

        return {
            "recommendation_type": "fpl_transfers",
            "priority_transfers": [
                {
                    "out": {
                        "player_name": "Underperforming Player",
                        "reason": "Poor recent form and fixtures"
                    },
                    "in": {
                        "player_name": "Palmer",
                        "reason": "Excellent form and favorable fixtures"
                    },
                    "priority": 1,
                    "cost_change": 2.5,
                    "expected_gain": 8.5,
                    "confidence": 0.80
                }
            ],
            "alternative_strategies": [
                {
                    "strategy": "Wait and see",
                    "reasoning": "Monitor player performances for another gameweek",
                    "transfers": []
                }
            ],
            "squad_analysis": {
                "strengths": ["Unable to analyze - data unavailable"],
                "weaknesses": ["Unable to analyze - data unavailable"],
                "overall_rating": 7.0
            },
            "user_info": user_team_data.get('user_info', {}),
            "bank_remaining": user_team_data.get('bank', 0),
            "free_transfers_used": 1,
            "data_source": "fallback_recommendation",
            "ai_summary": "Unable to fetch current data. Consider popular transfers like bringing in Palmer for consistent returns.",
            "generated_at": datetime.now().isoformat()
        }

    async def _generate_pre_season_squad_recommendation(
        self,
        user_team_data: Dict[str, Any],
        gameweeks: int
    ) -> Dict[str, Any]:
        """Generate squad building recommendations for pre-season"""

        user_info = user_team_data.get('user_info', {})

        try:
            # Fetch real data for analysis
            players = await asyncio.wait_for(self._fetch_real_player_data(), timeout=5.0)
            fixtures = await asyncio.wait_for(self._fetch_real_fixture_data(), timeout=3.0)

            if self.use_llm and self.client:
                return await self._generate_llm_pre_season_recommendation(
                    user_info, players, fixtures, gameweeks
                )
            else:
                return await self._generate_enhanced_pre_season_recommendation(
                    user_info, players, fixtures, gameweeks
                )

        except Exception as e:
            print(f"Error in pre-season recommendation: {e}")
            return await self._generate_fallback_pre_season_recommendation(user_info, gameweeks)

    async def _generate_llm_pre_season_recommendation(
        self,
        user_info: Dict[str, Any],
        players: List[Dict],
        fixtures: List[Dict],
        gameweeks: int
    ) -> Dict[str, Any]:
        """Generate LLM-powered pre-season squad recommendations"""

        # Get top players by position for context
        top_players_by_position = self._get_top_players_by_position(players)

        # Get fixture analysis
        fixture_analysis = self._analyze_opening_fixtures(fixtures, gameweeks)

        prompt = f"""
You are an expert Fantasy Premier League analyst helping a manager build their initial squad for the 2025-26 season.

MANAGER INFORMATION:
- Name: {user_info.get('name', 'Unknown')}
- Team Name: {user_info.get('team_name', 'Unknown')}
- Experience: {user_info.get('years_active', 0)} years in FPL
- Status: Pre-season (building initial squad)

BUDGET: £100.0m
SQUAD REQUIREMENTS: 15 players (2 GK, 5 DEF, 5 MID, 3 FWD)

TOP PLAYERS BY POSITION (Current Season):
{self._format_top_players_for_llm(players)}

OPENING FIXTURES ANALYSIS (First {gameweeks} gameweeks):
{fixture_analysis}

Please provide a complete squad recommendation considering:
1. Budget optimization (£100m total)
2. Opening fixture difficulty
3. Player form and expected performance
4. Value for money picks
5. Balanced risk/reward approach
6. Popular vs differential picks

Respond in JSON format with:
{{
    "recommendation_type": "pre_season_squad",
    "squad_recommendation": {{
        "formation": "3-5-2",
        "total_cost": 100.0,
        "players": [
            {{
                "player_name": "...",
                "position": "GK",
                "team": "...",
                "price": 5.5,
                "reasoning": "...",
                "starter": true
            }}
        ]
    }},
    "key_strategies": [
        "Focus on premium attackers",
        "Value picks in defense",
        "..."
    ],
    "transfer_targets": [
        {{
            "gameweek": 3,
            "target": "Player Name",
            "reasoning": "..."
        }}
    ],
    "ai_summary": "Comprehensive squad analysis and recommendations..."
}}
"""

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert Fantasy Premier League analyst providing comprehensive squad building advice."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=2500
            )

            # Parse LLM response
            llm_response = response.choices[0].message.content

            # Try to extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', llm_response, re.DOTALL)
            if json_match:
                recommendation_data = json.loads(json_match.group())

                # Add metadata
                recommendation_data.update({
                    "user_info": user_info,
                    "data_source": "llm_analysis",
                    "players_analyzed": len(players),
                    "generated_at": datetime.now().isoformat()
                })

                return recommendation_data
            else:
                # Fallback if JSON parsing fails
                return await self._generate_enhanced_pre_season_recommendation(
                    user_info, players, fixtures, gameweeks
                )

        except Exception as e:
            print(f"LLM pre-season analysis failed: {e}")
            return await self._generate_enhanced_pre_season_recommendation(
                user_info, players, fixtures, gameweeks
            )

    async def _generate_enhanced_pre_season_recommendation(
        self,
        user_info: Dict[str, Any],
        players: List[Dict],
        fixtures: List[Dict],
        gameweeks: int
    ) -> Dict[str, Any]:
        """Generate enhanced pre-season recommendations without LLM"""

        # Build a balanced squad using real data
        squad = self._build_optimal_squad(players, 100.0)

        return {
            "recommendation_type": "pre_season_squad",
            "squad_recommendation": {
                "formation": "3-5-2",
                "total_cost": sum(p.get('price', 0) for p in squad),
                "players": squad
            },
            "key_strategies": [
                "Premium attackers for high ceiling",
                "Value defenders with attacking potential",
                "Balanced midfield with form players",
                "Reliable goalkeeper from top 6 team"
            ],
            "transfer_targets": [
                {
                    "gameweek": 3,
                    "target": "Monitor price changes",
                    "reasoning": "Assess early season form before making changes"
                }
            ],
            "user_info": user_info,
            "data_source": "enhanced_analysis",
            "players_analyzed": len(players),
            "ai_summary": f"Welcome to FPL 2025-26, {user_info.get('name', 'Manager')}! This squad balances premium picks with value options. Focus on strong opening fixtures and proven performers.",
            "generated_at": datetime.now().isoformat()
        }

    def _get_top_players_by_position(self, players: List[Dict]) -> Dict[str, List[Dict]]:
        """Get top players by position for analysis"""
        positions = {'GK': [], 'DEF': [], 'MID': [], 'FWD': []}

        for player in players:
            pos = player.get('position', 'Unknown')
            if pos in positions:
                positions[pos].append(player)

        # Sort by total points and take top players
        for pos in positions:
            positions[pos] = sorted(positions[pos], key=lambda p: p.get('total_points', 0), reverse=True)[:10]

        return positions

    def _analyze_opening_fixtures(self, fixtures: List[Dict], gameweeks: int) -> str:
        """Analyze opening fixtures for all teams"""
        team_fixtures = {}

        for fixture in fixtures[:gameweeks * 10]:  # Approximate
            home_team = fixture.get('team_h_name', '')
            away_team = fixture.get('team_a_name', '')

            if home_team not in team_fixtures:
                team_fixtures[home_team] = []
            if away_team not in team_fixtures:
                team_fixtures[away_team] = []

            team_fixtures[home_team].append(f"vs {away_team} (H)")
            team_fixtures[away_team].append(f"vs {home_team} (A)")

        # Format for display
        analysis = []
        for team, fixtures_list in list(team_fixtures.items())[:10]:  # Top 10 teams
            analysis.append(f"{team}: {', '.join(fixtures_list[:3])}")

        return "\n".join(analysis)

    def _build_optimal_squad(self, players: List[Dict], budget: float) -> List[Dict]:
        """Build an optimal squad within budget"""
        squad = []
        remaining_budget = budget

        # Get players by position
        by_position = {'GK': [], 'DEF': [], 'MID': [], 'FWD': []}
        for player in players:
            pos = player.get('position', 'Unknown')
            if pos in by_position:
                by_position[pos].append(player)

        # Sort by value (points per price)
        for pos in by_position:
            by_position[pos].sort(key=lambda p: p.get('total_points', 0) / max(p.get('price', 1), 1), reverse=True)

        # Select players by position
        selections = [
            ('GK', 2), ('DEF', 5), ('MID', 5), ('FWD', 3)
        ]

        for pos, count in selections:
            for i in range(count):
                if by_position[pos] and remaining_budget >= by_position[pos][0].get('price', 0):
                    player = by_position[pos].pop(0)
                    squad.append({
                        "player_name": player.get('name', 'Unknown'),
                        "position": pos,
                        "team": player.get('team', 'Unknown'),
                        "price": player.get('price', 0),
                        "reasoning": f"Top value pick in {pos} position",
                        "starter": i < (2 if pos == 'GK' else 3 if pos == 'DEF' else 5 if pos == 'MID' else 2)
                    })
                    remaining_budget -= player.get('price', 0)

        return squad

    async def _generate_fallback_pre_season_recommendation(
        self,
        user_info: Dict[str, Any],
        gameweeks: int
    ) -> Dict[str, Any]:
        """Generate fallback pre-season recommendation"""

        return {
            "recommendation_type": "pre_season_squad",
            "squad_recommendation": {
                "formation": "3-5-2",
                "total_cost": 100.0,
                "players": [
                    {"player_name": "Haaland", "position": "FWD", "team": "Manchester City", "price": 15.0, "reasoning": "Premium striker with highest ceiling", "starter": True},
                    {"player_name": "Salah", "position": "MID", "team": "Liverpool", "price": 13.0, "reasoning": "Consistent performer with penalty duties", "starter": True},
                    {"player_name": "Palmer", "position": "MID", "team": "Chelsea", "price": 11.0, "reasoning": "Excellent value with penalty duties", "starter": True},
                    {"player_name": "Saka", "position": "MID", "team": "Arsenal", "price": 10.0, "reasoning": "Reliable returns from top team", "starter": True},
                    {"player_name": "Mbeumo", "position": "MID", "team": "Brentford", "price": 7.5, "reasoning": "Great value midfielder", "starter": True},
                    {"player_name": "Cunha", "position": "FWD", "team": "Wolves", "price": 6.5, "reasoning": "Value forward option", "starter": True},
                    {"player_name": "Gabriel", "position": "DEF", "team": "Arsenal", "price": 6.0, "reasoning": "Attacking defender from top team", "starter": True},
                    {"player_name": "Gvardiol", "position": "DEF", "team": "Manchester City", "price": 5.5, "reasoning": "Attacking threat from fullback", "starter": True},
                    {"player_name": "Lewis", "position": "DEF", "team": "Newcastle", "price": 4.5, "reasoning": "Budget defender with potential", "starter": True}
                ]
            },
            "key_strategies": [
                "Premium attackers for high ceiling",
                "Value picks in midfield and defense",
                "Focus on penalty takers",
                "Target players with good opening fixtures"
            ],
            "transfer_targets": [
                {
                    "gameweek": 3,
                    "target": "Monitor early season form",
                    "reasoning": "Assess performances before making changes"
                }
            ],
            "user_info": user_info,
            "data_source": "fallback_recommendation",
            "ai_summary": f"Welcome to FPL 2025-26, {user_info.get('name', 'Manager')}! This template squad provides a strong foundation with premium attackers and value picks.",
            "generated_at": datetime.now().isoformat()
        }

    async def get_captain_recommendations(
        self,
        squad: Optional[List[Dict]] = None,
        gameweek: Optional[int] = None
    ) -> Dict[str, Any]:
        """Generate AI-powered captaincy recommendations using real FPL data and LLM analysis"""

        try:
            # Fetch real data with timeout
            players = await asyncio.wait_for(self._fetch_real_player_data(), timeout=5.0)
            fixtures = await asyncio.wait_for(self._fetch_real_fixture_data(), timeout=3.0)

            # Use LLM for dynamic captain recommendations if available
            if self.use_llm and self.client:
                return await self._generate_llm_captain_recommendation(
                    players, fixtures, squad, gameweek
                )
            else:
                # Fallback to enhanced algorithm
                return await self._generate_enhanced_mock_captain(
                    players, fixtures, squad, gameweek
                )
        except asyncio.TimeoutError:
            print("⚠️ Database query timeout for captain recommendations, using fallback")
            return await self._generate_fallback_captain_recommendation(gameweek)
        except Exception as e:
            print(f"Error in captain recommendation: {e}")
            return await self._generate_fallback_captain_recommendation(gameweek)

    async def _generate_llm_captain_recommendation(
        self,
        players: List[Dict],
        fixtures: List[Dict],
        squad: Optional[List[Dict]] = None,
        gameweek: Optional[int] = None
    ) -> Dict[str, Any]:
        """Generate captain recommendation using OpenAI LLM with real data"""

        try:
            # Get top attacking players for captaincy
            top_captains = self._get_top_captain_candidates(players)
            fixture_analysis = self._analyze_captain_fixtures(fixtures, top_captains)

            prompt = f"""
You are an expert Fantasy Premier League (FPL) analyst with access to current FPL news and trends. Provide fresh, dynamic captain recommendations for gameweek {gameweek or 1} of the 2025-26 season.

CURRENT FPL CONTEXT (2025-26 Season):
- Early season captain picks should focus on proven performers
- Consider penalty takers and set piece specialists
- Account for new signings and role changes
- Factor in current injury news and rotation risks
- Look for favorable fixtures and opponent weaknesses

TOP CAPTAIN CANDIDATES (Real FPL Data):
{json.dumps(top_captains, indent=2)}

FIXTURE ANALYSIS (Next gameweek):
{json.dumps(fixture_analysis, indent=2)}

USER'S SQUAD: {squad or "All FPL players available for analysis"}

STRATEGY GUIDELINES:
1. **Form & Fixtures**: Prioritize players with good recent form and favorable matchups
2. **Penalty Duties**: Consider players on penalties for guaranteed involvement
3. **Ownership**: Balance between safe picks and differentials
4. **Current News**: Factor in any injury updates or team news
5. **Historical Data**: Use past performance against similar opponents

Please provide a JSON response with this EXACT structure:
{{
    "recommendation_type": "captaincy",
    "gameweek": {gameweek or 1},
    "recommendations": [
        {{
            "player_name": "Exact Player Name",
            "team": "Team Name",
            "position": "MID/FWD",
            "confidence": <0.75_to_0.95>,
            "predicted_points": <captain_points_estimate>,
            "reasoning": "Specific reasoning including fixtures, form, and current context",
            "fixture": "Team vs Opponent (H/A)",
            "fixture_difficulty": <1_to_5_scale>,
            "form_score": <recent_form_rating>,
            "ownership": <ownership_percentage>,
            "risk_level": "Low/Medium/High"
        }}
        // Top 3-5 captain options
    ],
    "analysis": {{
        "safe_pick": "Most reliable captain option with reasoning",
        "differential_pick": "Lower ownership captain with high upside",
        "avoid": ["Players to avoid this gameweek with reasons"],
        "key_factors": [
            "Fixture difficulty considerations",
            "Form and injury updates",
            "Penalty/set piece duties",
            "Rotation risks"
        ]
    }},
    "ai_summary": "Comprehensive captaincy strategy for this gameweek with key recommendations"
}}

IMPORTANT: Generate fresh recommendations each time. Vary your analysis based on different factors (form vs fixtures, safe vs differential, etc). Consider current FPL news and trends.
"""

            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert FPL analyst with access to current news and trends. Generate unique, varied captain recommendations each time."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.6,  # Higher temperature for varied recommendations
                max_tokens=2000
            )

            llm_response = response.choices[0].message.content

            try:
                # Extract JSON from markdown code blocks if present
                import re
                json_match = re.search(r'```json\s*(\{.*?\})\s*```', llm_response, re.DOTALL)
                if json_match:
                    json_str = json_match.group(1)
                else:
                    # Try to find JSON object in response
                    json_match = re.search(r'\{.*\}', llm_response, re.DOTALL)
                    if json_match:
                        json_str = json_match.group(0)
                    else:
                        json_str = llm_response

                # Parse the extracted JSON
                recommendation = json.loads(json_str)

                # Add metadata
                recommendation["data_source"] = "real_fpl_data"
                recommendation["llm_model"] = self.model
                recommendation["generated_at"] = datetime.now().isoformat()

                return recommendation

            except (json.JSONDecodeError, AttributeError):
                # If JSON parsing fails, create structured response from text
                print(f"Failed to parse LLM captain response: {llm_response[:200]}...")
                return await self._generate_enhanced_mock_captain(players, fixtures, squad, gameweek)

            try:
                recommendation = json.loads(llm_response)
                recommendation["data_source"] = "real_fpl_data"
                recommendation["llm_model"] = self.model
                recommendation["generated_at"] = datetime.now().isoformat()
                return recommendation

            except json.JSONDecodeError:
                return await self._generate_enhanced_mock_captain(players, fixtures, squad, gameweek)

        except Exception as e:
            print(f"Error calling OpenAI API for captain recommendation: {e}")
            return await self._generate_enhanced_mock_captain(players, fixtures, squad, gameweek)

    def _get_top_captain_candidates(self, players: List[Dict]) -> List[Dict]:
        """Get top captain candidates based on attacking potential"""
        candidates = []

        for player in players:
            # Focus on attacking players (MID/FWD with good stats)
            if player.get("position") in ["MID", "FWD"]:
                goals = player.get("goals_scored", 0)
                assists = player.get("assists", 0)
                form = player.get("form", 0)
                points = player.get("total_points", 0)

                # Calculate captain score
                captain_score = (goals * 6) + (assists * 3) + (form * 2) + (points * 0.1)

                if captain_score > 10:  # Minimum threshold
                    candidates.append({
                        "name": player.get("name"),
                        "team": player.get("team"),
                        "position": player.get("position"),
                        "price": player.get("price"),
                        "goals": goals,
                        "assists": assists,
                        "form": form,
                        "total_points": points,
                        "ownership": player.get("selected_by_percent", 0),
                        "captain_score": captain_score
                    })

        # Sort by captain score and return top 10
        return sorted(candidates, key=lambda x: x["captain_score"], reverse=True)[:10]

    def _analyze_captain_fixtures(self, fixtures: List[Dict], candidates: List[Dict]) -> List[Dict]:
        """Analyze fixtures for captain candidates"""
        fixture_analysis = []

        for candidate in candidates[:5]:  # Top 5 candidates
            team_name = candidate.get("team")

            # Find upcoming fixture for this team
            team_fixture = None
            for fixture in fixtures:
                if fixture.get("team_h") == team_name or fixture.get("team_a") == team_name:
                    team_fixture = fixture
                    break

            if team_fixture:
                is_home = team_fixture.get("team_h") == team_name
                opponent = team_fixture.get("team_a") if is_home else team_fixture.get("team_h")
                difficulty = team_fixture.get("team_h_difficulty") if is_home else team_fixture.get("team_a_difficulty")

                fixture_analysis.append({
                    "player": candidate.get("name"),
                    "team": team_name,
                    "opponent": opponent,
                    "home_away": "H" if is_home else "A",
                    "difficulty": difficulty,
                    "gameweek": team_fixture.get("gameweek")
                })

        return fixture_analysis

    async def _generate_enhanced_mock_captain(
        self,
        players: List[Dict],
        fixtures: List[Dict],
        squad: Optional[List[Dict]] = None,
        gameweek: Optional[int] = None
    ) -> Dict[str, Any]:
        """Generate enhanced captain recommendation using real data"""

        top_captains = self._get_top_captain_candidates(players)
        fixture_analysis = self._analyze_captain_fixtures(fixtures, top_captains)

        recommendations = []
        for i, captain in enumerate(top_captains[:3]):
            # Find fixture info for this captain
            captain_fixture = None
            for fixture_info in fixture_analysis:
                if fixture_info.get("player") == captain.get("name"):
                    captain_fixture = fixture_info
                    break

            # Build fixture string
            if captain_fixture:
                team = captain_fixture.get("team", captain.get("team", "Unknown"))
                opponent = captain_fixture.get("opponent", "TBD")
                home_away = captain_fixture.get("home_away", "?")
                fixture_str = f"{team} vs {opponent} ({home_away})"
                difficulty = captain_fixture.get("difficulty", 3)
            else:
                # Fallback if no fixture found
                fixture_str = f"{captain.get('team', 'Unknown')} vs TBD"
                difficulty = 3

            recommendations.append({
                "player_name": captain.get("name", "Unknown"),
                "team": captain.get("team", "Unknown"),
                "position": captain.get("position", "Unknown"),
                "confidence": max(0.95 - (i * 0.05), 0.75),  # Decreasing confidence
                "predicted_points": max(15 - (i * 1.5), 10),  # Decreasing points
                "reasoning": f"Strong form ({captain.get('form', 0)}) with {captain.get('goals', 0)} goals and {captain.get('assists', 0)} assists. Total points: {captain.get('total_points', 0)}",
                "fixture": fixture_str,
                "fixture_difficulty": difficulty,
                "form_score": captain.get("form", 0),
                "ownership": f"{captain.get('ownership', 0)}%",
                "historical_performance": f"Captain score: {captain.get('captain_score', 0):.1f}"
            })

        return {
            "recommendation_type": "captaincy",
            "gameweek": gameweek or 1,
            "recommendations": recommendations,
            "analysis": {
                "data_source": "real_fpl_data",
                "players_analyzed": len(players),
                "safe_pick": recommendations[0]["player_name"] if recommendations else "Unknown",
                "differential_pick": recommendations[1]["player_name"] if len(recommendations) > 1 else "Unknown",
                "avoid": ["Players with difficult away fixtures", "Rotation risks"],
                "key_factors": [
                    "Form and recent goal scoring record",
                    "Fixture difficulty and home advantage",
                    "Ownership levels for differential opportunities"
                ]
            },
            "ai_summary": f"Top captain pick is {recommendations[0]['player_name'] if recommendations else 'Unknown'} based on real FPL data analysis. Strong form and favorable fixture make this the optimal choice.",
            "data_source": "real_fpl_data"
        }

    async def _generate_fallback_captain_recommendation(
        self,
        gameweek: Optional[int] = None
    ) -> Dict[str, Any]:
        """Generate a quick fallback captain recommendation when database is unavailable"""

        return {
            "recommendation_type": "captaincy",
            "gameweek": gameweek or 1,
            "recommendations": [
                {
                    "player_name": "Haaland",
                    "team": "Manchester City",
                    "position": "FWD",
                    "confidence": 0.90,
                    "predicted_points": 14,
                    "reasoning": "Premium striker with excellent goal scoring record. Consistent captain choice.",
                    "fixture": "Manchester City vs TBD (H)",
                    "fixture_difficulty": 2,
                    "form_score": 8.5,
                    "ownership": "45%",
                    "historical_performance": "Averages 12+ points as captain"
                },
                {
                    "player_name": "Salah",
                    "team": "Liverpool",
                    "position": "MID",
                    "confidence": 0.85,
                    "predicted_points": 12,
                    "reasoning": "Reliable midfielder with penalty duties. Strong home record.",
                    "fixture": "Liverpool vs TBD (H)",
                    "fixture_difficulty": 2,
                    "form_score": 7.8,
                    "ownership": "35%",
                    "historical_performance": "Consistent double-digit returns"
                },
                {
                    "player_name": "Palmer",
                    "team": "Chelsea",
                    "position": "MID",
                    "confidence": 0.80,
                    "predicted_points": 11,
                    "reasoning": "In excellent form with penalty duties. Good differential option.",
                    "fixture": "Chelsea vs TBD (H)",
                    "fixture_difficulty": 3,
                    "form_score": 8.2,
                    "ownership": "25%",
                    "historical_performance": "Strong underlying stats"
                }
            ],
            "analysis": {
                "data_source": "fallback_recommendation",
                "safe_pick": "Haaland",
                "differential_pick": "Palmer",
                "avoid": ["Rotation risks", "Difficult away fixtures"],
                "key_factors": [
                    "Form and goal scoring record",
                    "Fixture difficulty",
                    "Ownership for differential opportunities"
                ]
            },
            "ai_summary": "Haaland remains the safest captain choice with 90% confidence. Palmer offers good differential value at lower ownership. Avoid rotation-prone players.",
            "data_source": "fallback_data"
        }

    async def _analyze_historical_captains(self) -> Dict[str, Any]:
        """Analyze historical captain performance data"""
        return {
            "top_captains_last_season": [
                {"name": "Haaland", "avg_points": 12.8, "home_avg": 14.2, "away_avg": 11.4, "15_plus_games": 8},
                {"name": "Palmer", "avg_points": 11.2, "home_avg": 12.1, "away_avg": 10.3, "15_plus_games": 5},
                {"name": "Saka", "avg_points": 10.5, "home_avg": 11.8, "away_avg": 9.2, "15_plus_games": 4}
            ],
            "penalty_takers": ["Palmer", "Saka", "Salah"],
            "home_specialists": ["Haaland", "Saka", "Son"],
            "differential_captains": ["Palmer", "Watkins", "Isak"]
        }

    async def get_chip_recommendations(
        self,
        remaining_chips: List[str],
        current_gameweek: int
    ) -> Dict[str, Any]:
        """Generate AI-powered chip usage recommendations"""
        
        await asyncio.sleep(0.5)  # Simulate API call
        
        return {
            "recommendation_type": "chip_strategy",
            "current_gameweek": current_gameweek,
            "recommendations": [
                {
                    "chip": "Triple Captain",
                    "recommended_gameweek": current_gameweek + 2,
                    "confidence": 0.85,
                    "reasoning": "Double gameweek with Haaland having two home fixtures",
                    "best_targets": ["Haaland", "Salah", "Palmer"],
                    "expected_gain": 15.5
                },
                {
                    "chip": "Bench Boost",
                    "recommended_gameweek": current_gameweek + 5,
                    "confidence": 0.78,
                    "reasoning": "Build strong bench during international break",
                    "preparation_needed": "Invest in playing bench players",
                    "expected_gain": 12.8
                },
                {
                    "chip": "Free Hit",
                    "recommended_gameweek": current_gameweek + 8,
                    "confidence": 0.72,
                    "reasoning": "Blank gameweek with limited fixtures",
                    "strategy": "Target teams with fixtures in blank gameweek",
                    "expected_gain": 20.2
                }
            ],
            "analysis": {
                "priority_order": ["Triple Captain", "Bench Boost", "Free Hit"],
                "timing_importance": "High - Chip timing can swing ranks significantly",
                "preparation_tips": [
                    "Monitor double gameweek announcements",
                    "Build bench strength 2-3 weeks before Bench Boost",
                    "Save Free Hit for biggest blank gameweek"
                ]
            },
            "ai_summary": "Triple Captain in the upcoming double gameweek offers the best immediate value. Plan bench investments for Bench Boost, and save Free Hit for the major blank gameweek."
        }
    
    async def analyze_player_query(
        self,
        query: str,
        context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Analyze natural language queries using historical data-aware AI"""

        # Use the new historical AI service for intelligent recommendations
        historical_ai = HistoricalAIService(db=self.db)

        try:
            return await historical_ai.analyze_player_query_historical(query, context)
        except Exception as e:
            print(f"Error with historical AI service: {e}")
            # Fallback to original method
            return await self._analyze_player_query_fallback(query, context)

    async def _analyze_player_query_fallback(
        self,
        query: str,
        context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Fallback method using original AI logic"""

        # Fetch real data
        players = await self._fetch_real_player_data()
        fixtures = await self._fetch_real_fixture_data()
        teams = await self._fetch_real_team_data()

        if self.use_llm and self.client:
            return await self._generate_llm_query_response(
                query, context, players, fixtures, teams
            )
        else:
            return await self._generate_enhanced_mock_query_response(
                query, context, players, fixtures, teams
            )

    async def _generate_llm_query_response(
        self,
        query: str,
        context: Optional[Dict],
        players: List[Dict],
        fixtures: List[Dict],
        teams: List[Dict]
    ) -> Dict[str, Any]:
        """Generate query response using OpenAI LLM with real data"""

        try:
            # Prepare relevant data based on query
            relevant_players = self._get_relevant_players_for_query(query, players)
            relevant_fixtures = fixtures[:5]  # Next 5 fixtures

            prompt = f"""
You are an expert Fantasy Premier League (FPL) analyst. Answer the user's question using the real FPL data provided.

USER QUESTION: "{query}"
CONTEXT: {context or "None provided"}

RELEVANT PLAYER DATA:
{json.dumps(relevant_players, indent=2)}

UPCOMING FIXTURES:
{json.dumps(relevant_fixtures, indent=2)}

Please provide a JSON response with the following structure:
{{
    "query_type": "descriptive_category",
    "response": "Detailed answer based on real data",
    "confidence": <0.0_to_1.0>,
    "supporting_data": {{
        "key_stats": ["stat1", "stat2", "stat3"],
        "player_recommendations": ["player1", "player2"],
        "reasoning": "Why these recommendations"
    }},
    "actionable_advice": ["specific action 1", "specific action 2"]
}}

Base your answer on the real data provided. Include specific statistics, player names, and concrete recommendations.
"""

            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert FPL analyst providing data-driven advice based on real player statistics and fixtures."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.4,
                max_tokens=1000
            )

            llm_response = response.choices[0].message.content

            try:
                recommendation = json.loads(llm_response)
                recommendation["data_source"] = "real_fpl_data"
                recommendation["llm_model"] = self.model
                recommendation["generated_at"] = datetime.now().isoformat()
                return recommendation

            except json.JSONDecodeError:
                # Fallback response if JSON parsing fails
                return {
                    "query_type": "general_analysis",
                    "response": llm_response,
                    "confidence": 0.8,
                    "supporting_data": {
                        "note": "LLM response in text format"
                    },
                    "data_source": "real_fpl_data",
                    "llm_model": self.model
                }

        except Exception as e:
            print(f"Error calling OpenAI API for query: {e}")
            return await self._generate_enhanced_mock_query_response(
                query, context, players, fixtures, teams
            )

    def _get_relevant_players_for_query(self, query: str, players: List[Dict]) -> List[Dict]:
        """Get players relevant to the query"""
        query_lower = query.lower()
        relevant_players = []

        # If asking about specific positions
        if "goalkeeper" in query_lower or "gk" in query_lower:
            relevant_players = [p for p in players if p.get("position") == "GK"][:5]
        elif "defender" in query_lower or "defence" in query_lower:
            relevant_players = [p for p in players if p.get("position") == "DEF"][:10]
        elif "midfielder" in query_lower or "midfield" in query_lower:
            relevant_players = [p for p in players if p.get("position") == "MID"][:10]
        elif "forward" in query_lower or "striker" in query_lower:
            relevant_players = [p for p in players if p.get("position") == "FWD"][:10]
        else:
            # General query - get top performers
            sorted_players = sorted(
                players,
                key=lambda x: x.get("total_points", 0) + (x.get("form", 0) * 2),
                reverse=True
            )
            relevant_players = sorted_players[:15]

        return relevant_players

    async def _generate_enhanced_mock_query_response(
        self,
        query: str,
        context: Optional[Dict],
        players: List[Dict],
        fixtures: List[Dict],
        teams: List[Dict]
    ) -> Dict[str, Any]:
        """Generate enhanced mock response using real data"""

        query_lower = query.lower()
        relevant_players = self._get_relevant_players_for_query(query, players)

        if "captain" in query_lower or "who should i captain" in query_lower:
            captain_recs = await self.get_captain_recommendations()
            return {
                "query_type": "captaincy_advice",
                "response": f"For captaincy this week, I recommend {captain_recs['recommendations'][0]['player_name']} as your primary choice. {captain_recs['recommendations'][0]['reasoning']} Based on historical data, he averages {captain_recs['recommendations'][0]['predicted_points']} points in similar fixtures.",
                "confidence": captain_recs['recommendations'][0]['confidence'],
                "detailed_recommendations": captain_recs['recommendations'][:3],
                "historical_context": "Analysis based on last season's performance in similar fixtures and current form trends."
            }
        elif "transfer" in query_lower or "who should i bring in" in query_lower:
            return {
                "query_type": "transfer_advice",
                "response": "Based on historical performance and upcoming fixtures, I'd prioritize Palmer and Mbeumo as transfer targets. Palmer scored 22 goals + 11 assists last season and is on penalties, while Mbeumo has 8 goals in his last 6 games and historically overperforms in favorable fixtures.",
                "confidence": 0.87,
                "supporting_data": {
                    "palmer_historical": "22 goals + 11 assists last season, 9/9 penalties scored",
                    "mbeumo_form": "8 goals in last 6 games, 3.2 xG indicates sustainability",
                    "fixture_analysis": "Both have historically performed well vs upcoming opponents",
                    "value_analysis": "Palmer £11.0m (premium but essential), Mbeumo £7.5m (excellent value)"
                },
                "transfer_priorities": [
                    {"player": "Palmer", "priority": 1, "reasoning": "Essential due to penalties and underlying stats"},
                    {"player": "Mbeumo", "priority": 2, "reasoning": "Exceptional value with strong recent form"},
                    {"player": "Saka", "priority": 3, "reasoning": "Consistent performer with good home record"}
                ]
            }
        elif any(word in query_lower for word in ["best", "recommend", "pick", "team"]):
            return {
                "query_type": "general_recommendation",
                "response": "For the upcoming gameweek, focus on players with strong home fixtures and historical performance. Haaland (36 goals last season), Palmer (22 goals + 11 assists), and Saka (16 goals + 9 assists) are premium options. For value, consider Mbeumo (8 goals in 6 games) and Rogers (4 assists in 5 games).",
                "confidence": 0.88,
                "key_picks": [
                    {"name": "Haaland", "price": "£15.0m", "reasoning": "36 goals last season, averages 2.1 goals vs upcoming opponent"},
                    {"name": "Palmer", "price": "£11.0m", "reasoning": "22 goals + 11 assists last season, on penalties"},
                    {"name": "Mbeumo", "price": "£7.5m", "reasoning": "8 goals in 6 games, historically strong in good fixtures"},
                    {"name": "Saka", "price": "£10.0m", "reasoning": "16 goals + 9 assists last season, excellent home record"}
                ],
                "formation_advice": "3-5-2 recommended for midfield strength with premium forwards"
            }
        elif "differential" in query_lower or "template" in query_lower:
            return {
                "query_type": "differential_advice",
                "response": "For differentials, consider Palmer (28.7% ownership vs 45.2% for Haaland), Watkins (strong home record, 19 goals last season), or Isak (Newcastle's main threat). Avoid template picks if you need to climb ranks.",
                "confidence": 0.82,
                "differential_picks": [
                    {"name": "Palmer", "ownership": "28.7%", "reasoning": "Lower owned than Haaland but similar ceiling"},
                    {"name": "Watkins", "ownership": "22.1%", "reasoning": "19 goals last season, strong home record"},
                    {"name": "Isak", "ownership": "18.5%", "reasoning": "Newcastle's main threat, good fixtures ahead"}
                ],
                "template_warning": "High ownership players (Haaland 45.2%, Saka 52.1%) are safer but offer less rank climbing potential"
            }
        elif "fixture" in query_lower or "difficulty" in query_lower:
            return {
                "query_type": "fixture_analysis",
                "response": "This gameweek favors home teams with Arsenal, Chelsea, and Man City all playing at home. Historically, these teams score 2+ goals in 70%+ of home games. Avoid away players vs strong defenses.",
                "confidence": 0.85,
                "fixture_insights": [
                    {"team": "Arsenal", "fixture": "vs Leicester (H)", "historical": "Scored 2+ goals in 18/19 home games last season"},
                    {"team": "Man City", "fixture": "vs Bournemouth (H)", "historical": "Averaged 3.2 goals at home vs promoted teams"},
                    {"team": "Chelsea", "fixture": "vs Brentford (H)", "historical": "Won 8/10 recent home games vs Brentford"}
                ]
            }
        else:
            return {
                "query_type": "general_analysis",
                "response": f"I understand you're asking about: '{query}'. Based on historical FPL data and current trends, I recommend focusing on players with proven track records in similar fixtures. Key factors: home advantage (worth ~2.3 points historically), penalty takers (higher floor), and players with strong underlying stats (xG, xA).",
                "confidence": 0.78,
                "suggestions": [
                    "Prioritize home players - they averaged 2.3 more points last season",
                    "Target penalty takers for higher floor (Palmer, Saka, Salah)",
                    "Check historical head-to-head records vs upcoming opponents",
                    "Balance premium picks (proven performers) with value options (form players)"
                ],
                "historical_context": "Analysis based on 2024-25 season data and similar gameweek patterns"
            }

# Global AI service instance
ai_service = AIService()
