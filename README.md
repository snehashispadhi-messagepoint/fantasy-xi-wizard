# Fantasy XI Wizard 🏆

An intelligent Fantasy Premier League (FPL) assistant powered by historical data analysis and AI recommendations. Get data-driven insights for team selection, captain choices, and transfer decisions.

## ✨ Features

### 🧠 **AI-Powered Recommendations**
- **Historical Data Intelligence**: Uses 2024-25 and 2023-24 season data for early season predictions
- **Progressive Learning**: Adapts from historical to current season data as gameweeks progress
- **Player Availability Checking**: Only recommends available players, excludes injured/transferred players
- **Team Change Awareness**: Considers club transfers and adaptation periods

### 🏆 **Team Management**
- **Complete Team Selection**: 11-player lineups with formation support (3-5-2, 4-4-2, 3-4-3, 4-5-1)
- **Budget Optimization**: £100m budget management with remaining funds tracking
- **Captain Recommendations**: Data-driven captain choices based on historical performance
- **Transfer Suggestions**: Value-based transfer recommendations with points-per-million analysis

### 📊 **Data & Analytics**
- **Live FPL Data**: Real-time sync with official Fantasy Premier League API
- **Historical Performance**: 300+ players with complete 2024-25 season statistics
- **Fixture Analysis**: Upcoming fixtures with difficulty ratings
- **Risk Assessment**: Player risk levels based on availability, injuries, and team changes

### 💬 **Interactive AI Chat**
- **Natural Language Queries**: Ask questions in plain English
- **Structured Responses**: Beautiful, formatted team breakdowns (no JSON clutter)
- **Context-Aware**: Understands different query types (captain, transfers, team selection)
- **Light/Dark Mode**: Responsive design for both themes

## 🚀 Quick Start

### Prerequisites
- **Python 3.8+**
- **Node.js 16+**
- **PostgreSQL** (or SQLite for development)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/fantasy-xi-wizard.git
cd fantasy-xi-wizard
```

2. **Backend Setup**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. **Frontend Setup**
```bash
cd frontend
npm install
```

4. **Environment Configuration**
```bash
# Backend - create .env file
DATABASE_URL=postgresql://user:password@localhost/fpl_db
OPENAI_API_KEY=your_openai_api_key_here  # Optional for AI features

# Frontend - create .env file
REACT_APP_API_URL=http://localhost:8000
```

### Running the Application

1. **Start Backend**
```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

2. **Start Frontend**
```bash
cd frontend
npm start
```

3. **Access the Application**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## 🎯 Usage Examples

### AI Chat Queries
```
"Give me 11 players for next 5 gameweeks in 3-5-2 formation"
"Who should I captain this week?"
"Best value players under £8m?"
"Should I transfer out Haaland?"
```

### Expected AI Response
```
Team Selection (3-5-2)                    Total: £90.0m | Remaining: £10.0m

📍 GOALKEEPER
• Pickford (Everton) - £5.5m
  2024-25: 158 pts, reliable shot-stopper

📍 DEFENDERS
• Gvardiol (Man City) - £6.0m
  2024-25: 153 pts, 5G 0A

👑 Captain Recommendation
Salah (Liverpool) - 344 points in 2024-25
```

## 🛠 Tech Stack
- **Frontend**: React 18 + Tailwind CSS + React Query
- **Backend**: Python FastAPI + SQLAlchemy + PostgreSQL
- **AI**: Historical Data Analysis + OpenAI GPT-4o-mini (optional)
- **Data**: Official FPL API + Historical Performance Database

## 🤖 AI Intelligence

### Early Season (GW 1-5)
- **70% Historical Data**: 2024-25 season performance
- **20% Context Data**: 2023-24 season for consistency
- **10% Current Factors**: Prices, availability, team changes

### In-Season (GW 6+)
- **50% Current Form**: Recent gameweek performance
- **30% Season Total**: Current season cumulative stats
- **20% Historical Context**: Previous seasons for comparison

## 🏗️ Architecture

### Backend (Python/FastAPI)
- **FastAPI**: Modern, fast web framework
- **SQLAlchemy**: Database ORM with PostgreSQL
- **Historical AI Service**: Intelligent recommendations using historical data
- **FPL API Integration**: Live data synchronization
- **OpenAI Integration**: Enhanced AI responses (optional)

### Frontend (React)
- **React 18**: Modern UI framework
- **Tailwind CSS**: Utility-first styling
- **React Query**: Data fetching and caching
- **Dark/Light Mode**: Theme switching support
- **Responsive Design**: Mobile-friendly interface

### Database Schema
- **Players**: Current season player data
- **Historical Player Stats**: 2024-25 and 2023-24 performance data
- **Teams**: Premier League team information
- **Fixtures**: Match schedules and difficulty ratings
- **Season Config**: AI behavior and gameweek settings

## 🛠️ Development

### Project Structure
```
fantasy-xi-wizard/
├── backend/                 # Python FastAPI backend
│   ├── app/
│   │   ├── api/            # API routes
│   │   ├── db/             # Database models and migrations
│   │   ├── services/       # Business logic and AI services
│   │   └── core/           # Configuration and utilities
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── pages/          # Page components
│   │   ├── services/       # API services
│   │   └── utils/          # Utilities and helpers
└── docs/                   # Documentation
```

### Key Features Implemented
- ✅ Historical data-aware AI recommendations
- ✅ Player availability and transfer checking
- ✅ Beautiful structured chat responses
- ✅ Formation-specific team selection
- ✅ Budget optimization and tracking
- ✅ Light/dark mode support
- ✅ Real-time FPL data synchronization

## 📈 Roadmap

- [ ] **Advanced Analytics**: xG, xA, and advanced metrics
- [ ] **Fixture Difficulty**: Enhanced fixture analysis
- [ ] **User Accounts**: Save teams and track performance
- [ ] **Mobile App**: React Native mobile application
- [ ] **Social Features**: Share teams and compete with friends

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Fantasy Premier League API** for providing official data
- **OpenAI** for AI capabilities
- **React & FastAPI** communities for excellent frameworks

---

**Built with ❤️ for FPL managers who want data-driven success!** 🏆


