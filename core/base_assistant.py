"""
Enhanced SAM AI Assistant - Base Assistant Class
"""
import asyncio
import logging
import threading
import time
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
import json

from config.settings import *

@dataclass
class AssistantState:
    """Assistant state management"""
    is_listening: bool = False
    is_speaking: bool = False
    is_processing: bool = False
    current_mode: str = "normal"
    privacy_mode: bool = False
    user_authenticated: bool = False
    session_start: datetime = None
    last_activity: datetime = None

class BaseAssistant:
    """Base class for SAM AI Assistant"""
    
    def __init__(self):
        self.state = AssistantState()
        self.state.session_start = datetime.now()
        self.state.last_activity = datetime.now()
        
        # Initialize logging
        self.setup_logging()
        
        # Event system
        self.event_handlers: Dict[str, List[Callable]] = {}
        self.running = False
        
        # Memory and context
        self.conversation_history: List[Dict] = []
        self.user_preferences: Dict = {}
        self.learned_patterns: Dict = {}
        
        # Performance metrics
        self.metrics = {
            "commands_processed": 0,
            "errors_encountered": 0,
            "response_times": [],
            "user_satisfaction": []
        }
        
        self.logger.info("Base Assistant initialized")
    
    def setup_logging(self):
        """Setup logging configuration"""
        log_file = LOGS_DIR / f"sam_{datetime.now().strftime('%Y%m%d')}.log"
        
        logging.basicConfig(
            level=getattr(logging, SYSTEM_CONFIG["log_level"]),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def register_event_handler(self, event: str, handler: Callable):
        """Register event handler"""
        if event not in self.event_handlers:
            self.event_handlers[event] = []
        self.event_handlers[event].append(handler)
    
    def emit_event(self, event: str, data: Any = None):
        """Emit event to registered handlers"""
        if event in self.event_handlers:
            for handler in self.event_handlers[event]:
                try:
                    handler(data)
                except Exception as e:
                    self.logger.error(f"Error in event handler for {event}: {e}")
    
    def update_activity(self):
        """Update last activity timestamp"""
        self.state.last_activity = datetime.now()
    
    def add_to_conversation(self, role: str, content: str):
        """Add message to conversation history"""
        self.conversation_history.append({
            "timestamp": datetime.now().isoformat(),
            "role": role,
            "content": content
        })
        
        # Keep only recent conversation
        if len(self.conversation_history) > AI_CONFIG["context_window"] * 2:
            self.conversation_history = self.conversation_history[-AI_CONFIG["context_window"] * 2:]
    
    def get_context(self) -> str:
        """Get conversation context"""
        context = []
        for msg in self.conversation_history[-AI_CONFIG["context_window"]:]:
            context.append(f"{msg['role']}: {msg['content']}")
        return "\n".join(context)
    
    def learn_from_interaction(self, command: str, response: str, satisfaction: float):
        """Learn from user interactions"""
        pattern_key = command.lower().strip()
        
        if pattern_key not in self.learned_patterns:
            self.learned_patterns[pattern_key] = {
                "count": 0,
                "avg_satisfaction": 0,
                "responses": []
            }
        
        pattern = self.learned_patterns[pattern_key]
        pattern["count"] += 1
        pattern["avg_satisfaction"] = (
            (pattern["avg_satisfaction"] * (pattern["count"] - 1) + satisfaction) / pattern["count"]
        )
        pattern["responses"].append(response)
        
        # Keep only best responses
        if len(pattern["responses"]) > 5:
            pattern["responses"] = pattern["responses"][-5:]
    
    def save_user_data(self):
        """Save user preferences and learned patterns"""
        try:
            user_data = {
                "preferences": self.user_preferences,
                "learned_patterns": self.learned_patterns,
                "metrics": self.metrics
            }
            
            with open(DATA_DIR / "user_data.json", "w") as f:
                json.dump(user_data, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Error saving user data: {e}")
    
    def load_user_data(self):
        """Load user preferences and learned patterns"""
        try:
            user_data_file = DATA_DIR / "user_data.json"
            if user_data_file.exists():
                with open(user_data_file, "r") as f:
                    user_data = json.load(f)
                
                self.user_preferences = user_data.get("preferences", {})
                self.learned_patterns = user_data.get("learned_patterns", {})
                self.metrics = user_data.get("metrics", self.metrics)
                
        except Exception as e:
            self.logger.error(f"Error loading user data: {e}")
    
    async def start(self):
        """Start the assistant"""
        self.running = True
        self.load_user_data()
        self.logger.info("Assistant started")
        self.emit_event("assistant_started")
    
    async def stop(self):
        """Stop the assistant"""
        self.running = False
        self.save_user_data()
        self.logger.info("Assistant stopped")
        self.emit_event("assistant_stopped")
    
    def get_status(self) -> Dict:
        """Get current assistant status"""
        return {
            "state": self.state.__dict__,
            "uptime": (datetime.now() - self.state.session_start).total_seconds(),
            "metrics": self.metrics,
            "features_enabled": FEATURES
        }