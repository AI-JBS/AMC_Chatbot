"""Main entry point for the Asset Management Chatbot API server."""

import uuid
import logging
from datetime import datetime
from typing import Dict, List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from react_agent.lifespan import lifespan
from react_agent.graph import make_graph
from react_agent.configuration import APP_STATE
from langchain_core.runnables import RunnableConfig

# Configure detailed logging with UTF-8 encoding
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('chatbot.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

# Pydantic V2 models for API requests/responses
class ChatMessage(BaseModel):
    role: str = Field(..., description="Message role: 'user' or 'assistant'")
    content: str = Field(..., description="Message content")
    timestamp: datetime = Field(default_factory=datetime.now)

class ChatRequest(BaseModel):
    message: str = Field(..., description="User message")
    session_id: Optional[str] = Field(None, description="Session ID for conversation continuity")
    user_context: Optional[Dict] = Field(default_factory=dict, description="Additional user context")

class ChatResponse(BaseModel):
    response: str = Field(..., description="Assistant response")
    session_id: str = Field(..., description="Session ID")
    message_id: str = Field(..., description="Unique message identifier")
    response_type: Optional[str] = Field(None, description="Type of response from tools")
    timestamp: datetime = Field(default_factory=datetime.now)

class HealthResponse(BaseModel):
    status: str = Field(..., description="Health status")
    version: str = Field(..., description="API version")
    timestamp: datetime = Field(default_factory=datetime.now)

# Initialize FastAPI app with lifespan for proper startup/shutdown
app = FastAPI(
    title="Asset Management Chatbot API",
    description="AI-powered financial advisor specializing in mutual fund investments 🏦💼",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory session storage (use Redis in production)
active_sessions: Dict[str, Dict] = {}

@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint for health check."""
    return HealthResponse(
        status="healthy",
        version="1.0.0"
    )

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        version="1.0.0"
    )

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """Main chat endpoint for conversation with the financial advisor."""
    logger.info(f"[CHAT REQUEST] Message: {request.message}")
    logger.info(f"[CHAT REQUEST] Session: {request.session_id}")
    try:
        # Generate session ID if not provided
        session_id = request.session_id or str(uuid.uuid4())
        message_id = str(uuid.uuid4())
        
        # Initialize session if new
        if session_id not in active_sessions:
            active_sessions[session_id] = {
                "messages": [],
                "context": request.user_context or {},
                "created_at": datetime.now()
            }
        
        # Create configuration for the agent
        config = RunnableConfig(
            configurable={
                "model": "azure_openai/HKP-gpt-4o",
                "enable_memory": True,
                "selected_tools": []  # Empty list means use all tools
            },
            tags=[f"session:{session_id}"],
            metadata={"session_id": session_id, "user_context": request.user_context}
        )
        
        # Create and invoke the agent
        graph = await make_graph(config)
        
        # Prepare input for the agent - include conversation history
        session_messages = active_sessions[session_id]["messages"]
        conversation_history = []
        
        # Convert session messages to the format expected by the agent
        for msg in session_messages:
            conversation_history.append({
                "role": msg.role,
                "content": msg.content
            })
        
        # Handle special lead collection messages
        processed_message = request.message
        if request.message.startswith("LEAD_SUBMIT:"):
            # Extract form data and call handle_lead_response
            try:
                import json
                form_data_str = request.message.replace("LEAD_SUBMIT:", "").strip()
                form_data = json.loads(form_data_str)
                processed_message = f"Please handle my lead submission with the following data: {json.dumps(form_data)}"
                logger.info(f"[LEAD_SUBMIT] Form data: {form_data}")
            except json.JSONDecodeError:
                processed_message = "I want to submit my lead information"
                logger.error("[LEAD_SUBMIT] Failed to parse form data")
        elif request.message == "LEAD_DECLINE":
            processed_message = "I prefer not to share my contact information at this time"
            logger.info("[LEAD_DECLINE] User declined lead collection")
        elif request.message == "LEAD_CLOSE":
            processed_message = "I want to close the lead collection form"
            logger.info("[LEAD_CLOSE] User closed lead form")

        # Add the current user message
        conversation_history.append({
            "role": "user",
            "content": processed_message
        })
        
        # For the first message in a session, just send the current message
        # For subsequent messages, send the full conversation history
        if len(session_messages) == 0:
            agent_input = {
                "messages": [{"role": "user", "content": request.message}]
            }
        else:
            agent_input = {
                "messages": conversation_history
            }
        
        # Invoke the agent with session-based memory
        logger.info(f"[AGENT] Invoking with input: {agent_input}")
        logger.info(f"[MEMORY] Session {session_id} has {len(session_messages)} previous messages")
        result = await graph.ainvoke(
            agent_input,
            config={
                **config,
                "thread_id": session_id  # Use session_id as thread_id for memory
            }
        )
        # Log result without potentially problematic Unicode characters
        result_summary = f"Messages: {len(result.get('messages', []))}, Last message type: {type(result.get('messages', [{}])[-1]).__name__ if result.get('messages') else 'None'}"
        logger.info(f"[AGENT] Result obtained: {result_summary}")
        
        # Extract the assistant response
        response_content = ""
        response_type = None
        
        if "messages" in result and result["messages"]:
            last_message = result["messages"][-1]
            response_content = last_message.content if hasattr(last_message, 'content') else str(last_message)
            
            # Extract response type from tool outputs in the conversation
            for message in result["messages"]:
                if hasattr(message, 'name') and hasattr(message, 'content'):
                    # This is a tool message
                    try:
                        import json
                        tool_output = json.loads(message.content)
                        if 'type' in tool_output:
                            response_type = tool_output['type']
                            logger.info(f"[RESPONSE_TYPE] Extracted from tool: {response_type}")
                            
                            # If we have structured data, ensure the final response includes it
                            if response_type in ['recommendation', 'comparison', 'performance_analysis', 'market_insights', 'consistency_analysis', 'correlation_analysis', 'portfolio', 'smart_recommendation', 'fee_analysis', 'fund_screening', 'opportunity_scan', 'smart_alerts', 'lead_collection', 'lead_submitted', 'lead_declined', 'lead_collection_declined', 'lead_already_submitted', 'quiz']:
                                # Append the JSON to the response content if not already there
                                json_str = json.dumps(tool_output, ensure_ascii=False)
                                if json_str not in response_content:
                                    response_content += f"\n\n{json_str}"
                                    logger.info(f"[JSON_APPENDED] Added structured data to response")
                            break
                    except (json.JSONDecodeError, AttributeError):
                        continue
        
        # Add user message to session (only the current one, not the full history)
        user_message = ChatMessage(role="user", content=request.message)
        active_sessions[session_id]["messages"].append(user_message)
        
        # Add assistant response to session
        assistant_message = ChatMessage(role="assistant", content=response_content)
        active_sessions[session_id]["messages"].append(assistant_message)
        
        # Log content without emojis to avoid Unicode issues
        safe_content = response_content[:100].encode('ascii', 'ignore').decode('ascii')
        logger.info(f"[RESPONSE] Content: {safe_content}...")
        logger.info(f"[RESPONSE] Type: {response_type}")
        
        return ChatResponse(
            response=response_content,
            session_id=session_id,
            message_id=message_id,
            response_type=response_type
        )
        
    except Exception as e:
        logger.error(f"[ERROR] Chat processing failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Chat processing error: {str(e)}")

@app.get("/sessions/{session_id}/history")
async def get_chat_history(session_id: str):
    """Get chat history for a specific session."""
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {
        "session_id": session_id,
        "messages": active_sessions[session_id]["messages"],
        "context": active_sessions[session_id]["context"],
        "created_at": active_sessions[session_id]["created_at"]
    }

@app.delete("/sessions/{session_id}")
async def clear_session(session_id: str):
    """Clear a specific chat session."""
    if session_id in active_sessions:
        del active_sessions[session_id]
        return {"message": f"Session {session_id} cleared successfully"}
    else:
        raise HTTPException(status_code=404, detail="Session not found")

@app.get("/tools")
async def get_available_tools():
    """Get list of available tools and their descriptions."""
    if not hasattr(APP_STATE, 'tool_names'):
        return {"tools": [], "message": "Tools not initialized"}
    
    return {
        "tools": APP_STATE.tool_names,
        "description": "Available financial advisory tools"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8022,
        reload=True,
        log_level="info"
    )