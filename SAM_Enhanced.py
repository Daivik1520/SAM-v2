"""
Enhanced SAM AI Assistant - Main Application
"""
import asyncio
import logging
import sys
import threading
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from core.base_assistant import BaseAssistant
from features.voice_control import VoiceController
from features.computer_vision import ComputerVisionController
from features.smart_home import SmartHomeController
from features.productivity import ProductivityController
from features.entertainment import EntertainmentController
from features.health_wellness import HealthWellnessController
from features.security import SecurityController
from ui.main_window import MainWindow
from config.settings import *

class EnhancedSAMAssistant(BaseAssistant):
    """Enhanced SAM AI Assistant with all features"""
    
    def __init__(self):
        super().__init__()
        
        # Initialize feature controllers
        self.initialize_features()
        
        # Initialize UI
        self.ui = None
        
        self.logger.info("Enhanced SAM Assistant initialized")
    
    def initialize_features(self):
        """Initialize all feature controllers"""
        try:
            # Voice Control
            if FEATURES["voice_control"]:
                self.voice_controller = VoiceController(self)
                self.logger.info("Voice control initialized")
            
            # Computer Vision
            if FEATURES["computer_vision"]:
                self.computer_vision = ComputerVisionController(self)
                self.logger.info("Computer vision initialized")
            
            # Smart Home
            if FEATURES["smart_home"]:
                self.smart_home_controller = SmartHomeController(self)
                self.logger.info("Smart home controller initialized")
            
            # Productivity
            if FEATURES["productivity"]:
                self.productivity_controller = ProductivityController(self)
                self.logger.info("Productivity controller initialized")
            
            # Entertainment
            if FEATURES["entertainment"]:
                self.entertainment_controller = EntertainmentController(self)
                self.logger.info("Entertainment controller initialized")
            
            # Health & Wellness
            if FEATURES["health_wellness"]:
                self.health_wellness_controller = HealthWellnessController(self)
                self.logger.info("Health & wellness controller initialized")
            
            # Security
            if FEATURES["security"]:
                self.security_controller = SecurityController(self)
                self.logger.info("Security controller initialized")
            
        except Exception as e:
            self.logger.error(f"Error initializing features: {e}")
    
    async def start(self):
        """Start the enhanced assistant"""
        try:
            await super().start()
            
            # Start feature controllers
            await self.start_features()
            
            # Initialize UI in main thread
            self.initialize_ui()
            
            self.logger.info("Enhanced SAM Assistant started successfully")
            
        except Exception as e:
            self.logger.error(f"Error starting assistant: {e}")
            raise
    
    async def start_features(self):
        """Start all feature controllers"""
        try:
            # Start voice control
            if hasattr(self, 'voice_controller'):
                await self.voice_controller.start_listening()
            
            # Start computer vision
            if hasattr(self, 'computer_vision'):
                self.computer_vision.start_camera()
            
            # Start smart home automation
            if hasattr(self, 'smart_home_controller'):
                self.smart_home_controller.start_automation()
            
            # Start productivity background services
            if hasattr(self, 'productivity_controller'):
                self.productivity_controller.start_background_services()
            
            # Start health monitoring
            if hasattr(self, 'health_wellness_controller'):
                self.health_wellness_controller.start_monitoring_services()
            
            # Start security monitoring
            if hasattr(self, 'security_controller'):
                self.security_controller.start_security_monitoring()
            
        except Exception as e:
            self.logger.error(f"Error starting features: {e}")
    
    def initialize_ui(self):
        """Initialize user interface"""
        try:
            self.ui = MainWindow(self)
            self.logger.info("UI initialized")
        except Exception as e:
            self.logger.error(f"Error initializing UI: {e}")
    
    async def stop(self):
        """Stop the enhanced assistant"""
        try:
            # Stop feature controllers
            await self.stop_features()
            
            await super().stop()
            
            self.logger.info("Enhanced SAM Assistant stopped")
            
        except Exception as e:
            self.logger.error(f"Error stopping assistant: {e}")
    
    async def stop_features(self):
        """Stop all feature controllers"""
        try:
            # Stop voice control
            if hasattr(self, 'voice_controller'):
                self.voice_controller.stop_listening()
            
            # Stop computer vision
            if hasattr(self, 'computer_vision'):
                self.computer_vision.stop_camera()
            
            # Stop smart home automation
            if hasattr(self, 'smart_home_controller'):
                self.smart_home_controller.stop_automation()
            
        except Exception as e:
            self.logger.error(f"Error stopping features: {e}")
    
    def run_ui(self):
        """Run the user interface"""
        if self.ui:
            self.ui.run()
    
    def get_comprehensive_status(self) -> Dict:
        """Get comprehensive status of all systems"""
        status = super().get_status()
        
        # Add feature-specific status
        if hasattr(self, 'voice_controller'):
            status['voice_control'] = self.voice_controller.get_voice_stats()
        
        if hasattr(self, 'computer_vision'):
            status['computer_vision'] = self.computer_vision.get_vision_stats()
        
        if hasattr(self, 'smart_home_controller'):
            status['smart_home'] = self.smart_home_controller.get_smart_home_stats()
        
        if hasattr(self, 'productivity_controller'):
            status['productivity'] = self.productivity_controller.get_productivity_stats()
        
        if hasattr(self, 'entertainment_controller'):
            status['entertainment'] = self.entertainment_controller.get_entertainment_stats()
        
        if hasattr(self, 'health_wellness_controller'):
            status['health_wellness'] = self.health_wellness_controller.get_health_wellness_stats()
        
        if hasattr(self, 'security_controller'):
            status['security'] = self.security_controller.get_security_status()
        
        return status


async def main():
    """Main application entry point"""
    try:
        # Create and start the enhanced assistant
        assistant = EnhancedSAMAssistant()
        
        # Start assistant in background
        await assistant.start()
        
        # Run UI in main thread
        def run_ui():
            assistant.run_ui()
        
        # Start UI in separate thread to avoid blocking
        ui_thread = threading.Thread(target=run_ui, daemon=False)
        ui_thread.start()
        
        # Keep the main thread alive
        ui_thread.join()
        
    except KeyboardInterrupt:
        print("\nShutting down SAM Assistant...")
    except Exception as e:
        logging.error(f"Fatal error: {e}")
        sys.exit(1)
    finally:
        if 'assistant' in locals():
            await assistant.stop()


if __name__ == "__main__":
    try:
        # Set up event loop for Windows compatibility
        if sys.platform.startswith('win'):
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        
        # Run the main application
        asyncio.run(main())
        
    except Exception as e:
        logging.error(f"Failed to start application: {e}")
        sys.exit(1)