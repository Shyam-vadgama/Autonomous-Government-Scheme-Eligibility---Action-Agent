# Government Scheme Eligibility & Action Agent

## 🏛️ Overview

An autonomous AI-powered agent system that acts as a **digital case worker** to help Indian citizens discover, evaluate eligibility, and apply for government schemes. Built using **Google Agent Development Kit (ADK)** patterns with **Google Gemini AI**.

## 🎯 Mission

Transform the complex landscape of Indian government schemes into accessible, personalized guidance for every citizen through autonomous AI agents.

## 🏗️ System Architecture

```
                    ┌─────────────────────────────────────────────────┐
                    │                ORCHESTRATOR                     │
                    └─────────────────┬───────────────────────────────┘
                                      │
            ┌─────────────────────────┼─────────────────────────────────┐
            │     ┌───────────────────▼──────────────┐                 │
            │  ┌──┤    Profile Analyzer Agent      ├──┐               │
            │  │  └─────────────────────────────────────┘  │               │
            │  │                                         │               │
            │  ▼                                         ▼               │
            │ ┌─────────────────────┐    ┌─────────────────────┐       │
            │ │ Scheme Discovery   │    │ Eligibility         │       │
            │ │ Agent              │    │ Reasoning Agent     │       │
            │ └─────────────────────┘    └─────────────────────┘       │
            │         │                             │                  │
            │         └──┬──────────────────────────┘                  │
            │            ▼                                             │
            │    ┌─────────────────────┐    ┌─────────────────────┐    │
            │    │ Action Planner      │    │ Follow-up Agent     │    │
            │    │ Agent               │    │                     │    │
            │    └─────────────────────┘    └─────────────────────┘    │
            └─────────────────────────────────────────────────────────────┘
```

## 🤖 Agent Capabilities

### 🎯 Profile Analyzer Agent
- Extracts demographic, economic, and social factors
- Identifies eligibility patterns and key characteristics
- Categorizes citizen profiles for targeted scheme matching

### 🔍 Scheme Discovery Agent
- Searches comprehensive government scheme database
- Matches schemes to profile characteristics using semantic analysis
- Ranks schemes by eligibility probability and relevance

### ⚖️ Eligibility Reasoning Agent
- Validates detailed eligibility criteria
- Checks income limits, age ranges, location requirements
- Provides confidence scores and gap analysis

### 📋 Action Planner Agent
- Generates step-by-step application plans
- Lists required documents and verification procedures
- Provides application deadlines and submission guidelines

### 📞 Follow-up Agent
- Tracks application status and progress
- Sends reminders and updates
- Suggests next steps and alternative schemes
- **SafeFailureHandler** - Graceful error handling and recovery

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Google Gemini AI API key
- Internet connection

### Installation

1. **Clone the repository:**
```bash
git clone <repository-url>
cd scheme-suggestor-agent
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Set up environment variables:**
```bash
# Create .env file
echo "GEMINI_API_KEY=your_api_key_here" > .env
```

4. **Get your Gemini API key:**
   - Visit [Google AI Studio](https://aistudio.google.com/apikey)
   - Create a new API key
   - Add it to your `.env` file

### Running the System

#### Option 1: Quick Start (Recommended)
```bash
python quick_start.py
```
- Automatically detects API quota availability
- Falls back to demo mode if quota is exhausted
- Starts web interface if API is available

#### Option 2: Demo Mode (No API calls)
```bash
python demo_mode.py
```
- Shows complete system architecture and capabilities
- Demonstrates sample workflow without consuming quota
- Perfect for understanding the system

#### Option 3: Full System (When quota available)
```bash
python main.py
```
- Runs complete agent initialization
- Requires available API quota
- Full functionality with real AI responses

## 🌐 Web Interface

Access the system through the web interface:

- **Main API**: http://localhost:8000
- **Demo Page**: http://localhost:8000/demo
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

### API Endpoints

```bash
# Analyze user profile
POST /api/v1/analyze-profile

# Find schemes and create application plan
POST /api/v1/apply-scheme  

# Follow up on applications
POST /api/v1/follow-up

# Get system status
GET /api/v1/status

# List available schemes
GET /api/v1/schemes
```

## 📝 Usage Examples

### Command Line Example
```python
# Test with sample farmer profile
python main.py
```

### Web Interface Example
```javascript
// Profile Analysis
const response = await fetch('/api/v1/analyze-profile', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({  
        user_input: "I am Ravi Kumar, 45 years old farmer from Gujarat with annual income of 80,000 rupees...",
        user_id: "user_123"
    })
});
```

### Sample User Input
```
"My name is Ravi Kumar. I am 45 years old, married with 2 children. 
I am a farmer in Gujarat with annual income of 80,000 rupees. 
I belong to OBC category. I have Aadhaar card and voter ID. 
I want to apply for agriculture related schemes and need financial help."
```

## 🎯 System Workflow

1. **User Input** → ProfileAnalyzerAgent converts to structured data
2. **Scheme Discovery** → SchemeDiscoveryAgent finds relevant schemes  
3. **Eligibility Check** → EligibilityReasoningAgent evaluates eligibility
4. **Action Planning** → ActionPlannerAgent creates step-by-step plans
5. **Response Generation** → System provides comprehensive guidance
6. **Follow-up Support** → FollowUpAgent tracks progress and provides updates

## 📊 Sample Output

```
🎉 ELIGIBILITY ANALYSIS COMPLETE

📋 PROFILE SUMMARY:
✅ Name: Ravi Kumar (Age: 45, State: Gujarat)
✅ Occupation: Farmer (Income: ₹80,000/year) 
✅ Category: OBC | Documents: Aadhaar, Voter ID

🌾 TOP RELEVANT SCHEMES:
1. PM-KISAN Samman Nidhi (95% relevance) - ✅ ELIGIBLE
2. Pradhan Mantri Fasal Bima Yojana (87% relevance) - ✅ ELIGIBLE  
3. Gujarat Kisan Sahay Scheme (82% relevance) - ✅ ELIGIBLE

💡 NEXT STEPS:
• Apply for PM-KISAN first (highest benefit: ₹6,000/year)
• Gather land ownership documents 
• Visit nearest Common Service Center
• Complete applications within 30 days for current cycle

⚡ Processing Time: 2,847ms | 📊 Confidence: 94.2%
```

## 🗂️ Project Structure

```
scheme-suggestor-agent/
├── agents/                    # Multi-agent system
│   ├── base_agent.py         # Google ADK base agent
│   ├── profile_analyzer.py   # Profile analysis agent  
│   ├── scheme_discovery.py   # Scheme discovery agent
│   ├── eligibility_reasoning.py # Eligibility assessment agent
│   ├── action_planner.py     # Action planning agent
│   └── follow_up_agent.py    # Follow-up and progress agent
├── config/                   # Configuration
│   ├── settings.py          # System settings
│   └── ollama_config.py     # Ollama integration
├── data/                    # Data and database
│   ├── schemes_db.py       # Government schemes database
│   └── user_profiles.py    # User profile models
├── tools/                  # System tools
│   └── system_tools.py    # Global utilities and tools
├── models/                # Data models  
│   └── agent_models.py   # Pydantic models
├── logs/                 # Application logs
├── main.py              # Main orchestrator
├── web_interface.py     # FastAPI web interface
├── setup.py            # Setup and installation script
├── requirements.txt    # Python dependencies
├── run.bat            # Windows run script
├── run.sh             # Linux/Mac run script
└── README.md         # This file
```

## ⚙️ Configuration

### Environment Variables (.env)
```bash
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2:7b
LOG_LEVEL=INFO
API_HOST=0.0.0.0  
API_PORT=8000
DEBUG=False
```

### Ollama Models
The system uses `llama2:7b` by default, but supports any Ollama model:
```bash
# Pull alternative models
ollama pull mistral:7b
ollama pull codellama:13b
```

## 🔧 Development

### Adding New Schemes
Add schemes to [data/schemes_db.py](data/schemes_db.py):
```python
{
    "scheme_id": "new_scheme_001",
    "name": "New Scheme Name", 
    "category": "agriculture",
    "description": "Scheme description...",
    "eligibility_criteria": {
        "age": {"min": 18, "max": 65},
        "income": {"max": 200000},
        "occupation": ["farmer"]
    }
}
```

### Extending Agents  
Create new agents by inheriting from `BaseAgent`:
```python
from agents.base_agent import BaseAgent

class CustomAgent(BaseAgent):
    def __init__(self):
        super().__init__("CustomAgent", "1.0.0")
        
    async def process_message(self, message: AgentMessage):
        # Custom agent logic
        pass
```

### Custom Rules
Add eligibility rules in [tools/system_tools.py](tools/system_tools.py):
```python
def evaluate_custom_rule(profile, scheme):
    # Custom eligibility logic
    return EligibilityResult(...)
```

## 📊 Performance & Monitoring

- **Response Time**: Typically 2-5 seconds per complete analysis
- **Concurrent Users**: Supports multiple simultaneous requests
- **Model Performance**: Optimized for accuracy vs speed balance
- **Memory Usage**: ~2-4GB with llama2:7b model loaded
- **Logging**: Comprehensive logging with loguru integration

## 🛡️ Security & Privacy

- **Local Processing**: All AI inference runs locally via Ollama
- **No Data Collection**: User data never leaves your system  
- **Secure by Design**: No external API calls for sensitive data
- **Audit Trail**: Complete decision logging for transparency
- **Error Handling**: Safe failure modes with data protection

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Google Agent Development Kit (ADK) for agent architecture patterns
- Ollama team for local language model infrastructure  
- Indian Government for open scheme information
- FastAPI for excellent web framework
- Pydantic for robust data validation

## 📞 Support

For support and questions:
- Open an issue on GitHub
- Check the [demo interface](http://localhost:8000/demo) for examples
- Review the API documentation at `/docs`

---

**Made with ❤️ for Indian Citizens** 

*Empowering citizens through AI-driven government scheme accessibility*