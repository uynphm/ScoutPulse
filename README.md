# ScoutPulse — AI-Powered Soccer Scouting Platform

ScoutPulse is an advanced soccer player analysis platform designed to empower scouts, coaches, and analysts with rich, AI-driven insights. By combining annotated soccer match video data with cutting-edge AI video and natural language processing technologies, ScoutPulse reveals player strengths, weaknesses, and key highlights through a sleek, intuitive interface.

## Key Features

- **Natural Language Search**: Users can search anything about a player—goals, assists, weaknesses, or specific match moments—and receive precise video clips plus AI-generated scouting reports.
- **AI-Powered Video Analysis**: Detects player actions and events from match videos, curates visual highlights of critical plays, and indexes semantic content for smart searching.
- **Interactive Video Player**: Seamlessly streams video highlights with overlaid AI insights on player performance metrics and event context.
- **Dynamic Player Reports**: Generates real-time, AI-written textual summaries of player performance, combining stats with tactical evaluation.
- **User-Friendly Dashboard**: Modern, responsive UI with filterable highlight lists, search suggestions, and easy navigation between players and matches.
- **Real-time Data Integration**: Live connection between frontend and backend with real player data and video highlights.

## Technology Stack

- **Frontend**: Next.js 15 with TypeScript, Tailwind CSS, and shadcn/ui components
- **Backend**: FastAPI with Python 3.13, SQLAlchemy ORM, and SQLite database
- **Database**: SQLite for development (easily configurable for PostgreSQL in production)
- **API Integration**: RESTful API with automatic data transformation between snake_case (backend) and camelCase (frontend)
- **Video Player**: HTML5 Video Player with interactive overlays and AI insights
- **Deployment**: Vercel for frontend hosting, FastAPI backend ready for cloud deployment

## Why ScoutPulse?

- Provides scouts with visual proof of player capabilities beyond raw statistics
- Combines video evidence and AI insight to quickly identify hidden talent and tactical fit
- Enables natural language interaction, making scouting accessible and efficient
- Bridges state-of-the-art AI technology and soccer expertise into a singular, cohesive platform

## Getting Started

### Prerequisites

- Node.js 18+ 
- Python 3.13+
- npm, yarn, pnpm, or bun
- pip (Python package manager)

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd ScoutPulse
```

2. **Backend Setup** (FastAPI):
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python3 seed_data.py  # Seed the database with sample data
python3 main.py  # Start the FastAPI server
```

3. **Frontend Setup** (Next.js):
```bash
cd scoutpulse
npm install
npm run dev
```

4. **Access the Application**:
   - Frontend: [http://localhost:3000](http://localhost:3000)
   - Backend API: [http://localhost:8000](http://localhost:8000)
   - API Documentation: [http://localhost:8000/docs](http://localhost:8000/docs)

### Quick Start with Setup Script

For automated setup, use the provided setup script:

```bash
cd backend
chmod +x setup.sh
./setup.sh
```

This will:
- Create a virtual environment
- Install all dependencies
- Initialize the database
- Seed with sample data
- Start the backend server

## Next Steps

- [ ] Build backend integration to fetch and analyze SoccerNet match data
- [ ] Develop AI pipelines for video highlight extraction and NLP-based report generation
- [ ] Design and implement frontend UI focusing on intuitive search and video playback
- [ ] Test platform internally with real queries, iterating based on scout feedback
- [ ] Integrate with AI services (Twelve Labs/IBM watsonx)
- [ ] Add user authentication and data persistence
- [ ] Implement advanced filtering and analytics features

## Learn More

- [Next.js Documentation](https://nextjs.org/docs) - learn about Next.js features and API
- [Tailwind CSS](https://tailwindcss.com/docs) - utility-first CSS framework
- [shadcn/ui](https://ui.shadcn.com/) - re-usable components built with Radix UI and Tailwind CSS

## Deploy on Vercel

The easiest way to deploy your Next.js app is to use the [Vercel Platform](https://vercel.com/new?utm_medium=default-template&filter=next.js&utm_source=create-next-app&utm_campaign=create-next-app-readme) from the creators of Next.js.

Check out our [Next.js deployment documentation](https://nextjs.org/docs/app/building-your-application/deploying) for more details.

---

**ScoutPulse** - Revolutionizing soccer scouting with AI-powered insights and video analysis.