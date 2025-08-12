# Asset Management Chatbot 🏦💼

A comprehensive AI-powered financial advisory platform featuring a modern chatbot widget for mutual fund investments and portfolio management. Built with FastAPI backend and Next.js frontend.

![Chatbot Demo](https://img.shields.io/badge/Status-Ready%20for%20Testing-green)
![Backend](https://img.shields.io/badge/Backend-FastAPI-blue)
![Frontend](https://img.shields.io/badge/Frontend-Next.js-black)
![AI](https://img.shields.io/badge/AI-Azure%20OpenAI-purple)

## 🌟 Features

### 💬 Intelligent Chat Widget
- **Floating Design**: Modern chat button in bottom-right corner (like customer service widgets)
- **Elder Brother Vibe**: Warm, supportive personality with emojis and PKR currency [[memory:3630232]]
- **Real-time Responses**: Powered by Azure OpenAI GPT-4o
- **Session Management**: Conversation continuity with memory
- **Beautiful UI**: Smooth animations and professional design

### 📊 Financial Advisory Tools
- **Smart Recommendations**: Risk-based mutual fund suggestions
- **Portfolio Analysis**: Performance trends and diversification analysis
- **Market Insights**: Real-time market alerts and opportunities
- **Risk Profiling**: Comprehensive risk tolerance assessment
- **Educational Content**: Financial terms and concepts explanation

### 🔧 Technical Excellence
- **Pydantic V2**: Modern data validation throughout [[memory:2688119]]
- **Single Entry Point**: One main.py file for easy deployment [[memory:4260123]]
- **Vector Search**: Pinecone integration for data retrieval [[memory:4260140]]
- **LangGraph**: Advanced agent workflow management
- **Type Safety**: Full TypeScript frontend

## 🚀 Quick Start

### Prerequisites
- **Python 3.9+** with pip
- **Node.js 18+** with npm
- **Azure OpenAI** access keys
- **Pinecone** account and API key

### 1. Backend Setup
```bash
# Navigate to backend
cd back-end

# Activate virtual environment [[memory:2372920]]
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
# Edit .env file with your API keys

# Start the server
python main.py
```

Backend will run on `http://localhost:8022` 

### 2. Frontend Setup
```bash
# Navigate to frontend
cd front-end

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend will run on `http://localhost:3022` 

### 3. Access the Application
- **Website**: Open [http://localhost:3000](http://localhost:3000)
- **Chat Widget**: Click the floating button in bottom-right corner
- **API Docs**: Visit [http://localhost:8000/docs](http://localhost:8000/docs)

## 📁 Project Structure

```
Asset Management Chatbot/
├── back-end/                          # FastAPI Backend
│   ├── main.py                       # Single entry point [[memory:4260123]]
│   ├── .env                          # Environment variables
│   ├── react_agent/                 # Core agent logic
│   │   ├── configuration.py         # Azure OpenAI & Pinecone config
│   │   ├── graph.py                 # LangGraph ReAct agent
│   │   ├── prompts.py               # Elder brother personality
│   │   ├── tools.py                 # Financial advisory tools
│   │   └── utils.py                 # Utility functions
│   ├── Data-Upsertion/              # Pinecone data management
│   └── Educational Data Processing/  # PDF processing for knowledge base
├── front-end/                        # Next.js Frontend  
│   ├── src/
│   │   ├── app/                     # Next.js App Router
│   │   ├── components/ChatWidget/   # Chat widget components
│   │   ├── hooks/useChat.ts         # Chat state management
│   │   ├── types/chat.ts            # TypeScript definitions
│   │   └── utils/api.ts             # Backend API client
│   ├── package.json
│   └── tailwind.config.js
└── Data/                             # Sample financial data
```

## 🎨 Chat Widget Design

The chatbot widget matches modern customer service chat interfaces:

### Visual Features
- **Floating Button**: 56x56px circle with gradient background
- **Smooth Animations**: Framer Motion powered transitions
- **Professional Colors**: Primary blue with financial green accents
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Tooltip Support**: Helpful hover messages

### Personality [[memory:3630232]]
- **Warm Greetings**: "Hey there! 👋 Welcome to your personal financial advisor"
- **Concise Responses**: 5-8 lines with semi-formal tone
- **Emoji Usage**: Appropriate financial emojis (📊💰🎯)
- **PKR Currency**: All financial data in Pakistani Rupees
- **Supportive Tone**: Elder sibling advisor approach

## 🔧 Configuration

### Backend Environment (.env)
```bash
# Azure OpenAI Configuration
AZURE_OPENAI_API_KEY=your_api_key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=HKP-gpt-4o
AZURE_OPENAI_TEMPERATURE=0.1

# Pinecone Configuration  
PINECONE_API_KEY=your_pinecone_key
PINECONE_INDEX_NAME=your-pinecone-index-name
```

### Frontend Environment (.env.local)
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME="Asset Management Chatbot"
```

## 🛠️ Development

### Running Tests
```bash
# Backend tests (from .venv) [[memory:2372920]]
cd back-end && python -m pytest tests/

# Frontend type checking
cd front-end && npm run type-check
```

### API Endpoints
- `POST /chat` - Send message to chatbot
- `GET /sessions/{id}/history` - Get chat history
- `DELETE /sessions/{id}` - Clear session
- `GET /health` - Health check
- `GET /tools` - Available financial tools

### Chat Widget API
```typescript
// Send message to chatbot
const response = await chatAPI.sendMessage({
  message: "What are the best mutual funds?",
  session_id: "optional-session-id",
  user_context: { platform: "web" }
});
```

## 🎯 Key Integrations

### Azure OpenAI
- **Model**: GPT-4o deployment
- **Temperature**: 0.1 for consistent financial advice
- **Embeddings**: text-embedding-3-small for vector search

### Pinecone Vector Database
- **Index**: hkp-amcdata for fund data
- **Namespaces**: consumer_21 for production data [[memory:2397179]]
- **Metadata**: Stored alongside vectors [[memory:4260140]]

### LangGraph Agent
- **ReAct Structure**: Reasoning and Action cycles [[memory:2355326]]
- **Memory**: Redis-backed conversation history
- **Tools**: 15+ financial advisory tools
- **Routing**: LLM-based decision making [[memory:2577842]]

## 📱 Mobile Responsiveness

The chat widget is fully responsive:
- **Mobile**: Compact interface with touch-friendly buttons
- **Tablet**: Medium-sized chat window
- **Desktop**: Full-featured interface with tooltips

## 🚀 Deployment

### Production Setup
1. **Backend**: Deploy FastAPI app with uvicorn
2. **Frontend**: Build and deploy Next.js static site
3. **Environment**: Update API URLs for production
4. **SSL**: Enable HTTPS for secure communication

### Docker Support (Optional)
```bash
# Backend Dockerfile
FROM python:3.9-slim
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
CMD ["python", "main.py"]

# Frontend Dockerfile  
FROM node:18-alpine
COPY . /app
WORKDIR /app
RUN npm install && npm run build
CMD ["npm", "start"]
```

## 🤝 Contributing

1. **Memory Updates**: Use update_memory tool for user preferences
2. **Elder Brother Tone**: Maintain warm, supportive personality
3. **PKR Currency**: All financial data in Pakistani Rupees
4. **Single Entry Point**: Keep main.py as only entry point
5. **Pydantic V2**: Use modern validation patterns

## 📄 License

This project is part of the Hysab Kytab personal financial management ecosystem [[memory:3329959]].

## 🆘 Troubleshooting

### Common Issues
1. **Backend Not Starting**: Check .env file and activate .venv [[memory:2372920]]
2. **Chat Widget Not Loading**: Verify API URL in frontend .env.local
3. **Azure OpenAI Errors**: Confirm API keys and deployment names
4. **Pinecone Connection**: Check API key and index name

### Support
- **Backend Logs**: Check console output from main.py
- **Frontend Errors**: Check browser developer console
- **API Testing**: Use /docs endpoint for manual testing

---

**Ready to transform financial advisory with AI! 🚀💼**

Start the servers and click the chat button to experience intelligent mutual fund advisory powered by Azure OpenAI.