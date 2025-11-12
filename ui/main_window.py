"""
Enhanced SAM AI Assistant - Main UI Window
"""
import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
import threading
import time
from datetime import datetime
from typing import Dict, List, Optional
import json
import logging
from PIL import Image, ImageTk
import numpy as np
import cv2

from core.base_assistant import BaseAssistant
from config.settings import UI_CONFIG, API_KEYS

class MainWindow:
    """Main application window with modern UI"""
    
    def __init__(self, assistant: BaseAssistant):
        self.assistant = assistant
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Set appearance mode and color theme
        ctk.set_appearance_mode(UI_CONFIG["appearance_mode"])
        ctk.set_default_color_theme(UI_CONFIG["color_theme"])
        
        # Create main window
        self.root = ctk.CTk()
        self.setup_window()
        
        # UI Components
        self.sidebar = None
        self.main_content = None
        self.status_bar = None
        self.chat_interface = None
        self.dashboard = None
        
        # State variables
        self.current_view = "dashboard"
        self.is_listening_indicator = False
        self.is_speaking_indicator = False
        
        # Initialize UI
        self.create_ui()
        self.setup_event_handlers()
        
        # Start UI update loop
        self.start_ui_updates()
    
    def setup_window(self):
        """Setup main window properties"""
        self.root.title("SAM - Smart AI Assistant")
        self.root.geometry(f"{UI_CONFIG['window_size'][0]}x{UI_CONFIG['window_size'][1]}")
        self.root.minsize(UI_CONFIG['min_window_size'][0], UI_CONFIG['min_window_size'][1])
        
        # Set window icon (if available)
        try:
            self.root.iconbitmap("assets/sam_icon.ico")
        except:
            pass
        
        # Configure grid
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
    
    def create_ui(self):
        """Create main UI components"""
        self.create_sidebar()
        self.create_main_content()
        self.create_status_bar()
    
    def create_sidebar(self):
        """Create sidebar with navigation and controls"""
        self.sidebar = ctk.CTkFrame(self.root, width=250, corner_radius=0)
        self.sidebar.grid(row=0, column=0, rowspan=2, sticky="nsew")
        self.sidebar.grid_rowconfigure(10, weight=1)
        
        # Logo/Title
        title_label = ctk.CTkLabel(
            self.sidebar, 
            text="SAM Assistant", 
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        # Status indicators
        self.create_status_indicators()
        
        # Navigation buttons
        self.create_navigation_buttons()
        
        # Control buttons
        self.create_control_buttons()
        
        # Settings button
        settings_btn = ctk.CTkButton(
            self.sidebar,
            text="Settings",
            command=self.show_settings,
            width=200
        )
        settings_btn.grid(row=11, column=0, padx=20, pady=10)
    
    def create_status_indicators(self):
        """Create status indicator widgets"""
        status_frame = ctk.CTkFrame(self.sidebar)
        status_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        
        # Listening indicator
        self.listening_indicator = ctk.CTkLabel(
            status_frame,
            text="🎤 Listening: OFF",
            font=ctk.CTkFont(size=12)
        )
        self.listening_indicator.grid(row=0, column=0, padx=10, pady=5)
        
        # Speaking indicator
        self.speaking_indicator = ctk.CTkLabel(
            status_frame,
            text="🔊 Speaking: OFF",
            font=ctk.CTkFont(size=12)
        )
        self.speaking_indicator.grid(row=1, column=0, padx=10, pady=5)
        
        # Security status
        self.security_indicator = ctk.CTkLabel(
            status_frame,
            text="🔒 Security: Normal",
            font=ctk.CTkFont(size=12)
        )
        self.security_indicator.grid(row=2, column=0, padx=10, pady=5)
    
    def create_navigation_buttons(self):
        """Create navigation buttons"""
        nav_buttons = [
            ("Dashboard", "dashboard", self.show_dashboard),
            ("Chat", "chat", self.show_chat),
            ("Voice Control", "voice", self.show_voice_control),
            ("Computer Vision", "vision", self.show_computer_vision),
            ("Smart Home", "smart_home", self.show_smart_home),
            ("Productivity", "productivity", self.show_productivity),
            ("Entertainment", "entertainment", self.show_entertainment),
            ("Health & Wellness", "health", self.show_health_wellness),
            ("Security", "security", self.show_security)
        ]
        
        self.nav_buttons = {}
        
        for i, (text, key, command) in enumerate(nav_buttons):
            btn = ctk.CTkButton(
                self.sidebar,
                text=text,
                command=command,
                width=200,
                height=35
            )
            btn.grid(row=i+2, column=0, padx=20, pady=5)
            self.nav_buttons[key] = btn
    
    def create_control_buttons(self):
        """Create control buttons"""
        control_frame = ctk.CTkFrame(self.sidebar)
        control_frame.grid(row=12, column=0, padx=20, pady=10, sticky="ew")
        
        # Voice control toggle
        self.voice_toggle = ctk.CTkSwitch(
            control_frame,
            text="Voice Control",
            command=self.toggle_voice_control
        )
        self.voice_toggle.grid(row=0, column=0, padx=10, pady=5)
        
        # Privacy mode toggle
        self.privacy_toggle = ctk.CTkSwitch(
            control_frame,
            text="Privacy Mode",
            command=self.toggle_privacy_mode
        )
        self.privacy_toggle.grid(row=1, column=0, padx=10, pady=5)
        
        # Camera toggle
        self.camera_toggle = ctk.CTkSwitch(
            control_frame,
            text="Camera",
            command=self.toggle_camera
        )
        self.camera_toggle.grid(row=2, column=0, padx=10, pady=5)
    
    def create_main_content(self):
        """Create main content area"""
        self.main_content = ctk.CTkFrame(self.root)
        self.main_content.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.main_content.grid_columnconfigure(0, weight=1)
        self.main_content.grid_rowconfigure(0, weight=1)
        
        # Create different views
        self.create_dashboard()
        self.create_chat_interface()
        self.create_voice_control_view()
        self.create_computer_vision_view()
        self.create_smart_home_view()
        self.create_productivity_view()
        self.create_entertainment_view()
        self.create_health_wellness_view()
        self.create_security_view()
        
        # Show dashboard by default
        self.show_dashboard()
    
    def create_status_bar(self):
        """Create status bar"""
        self.status_bar = ctk.CTkFrame(self.root, height=30)
        self.status_bar.grid(row=1, column=1, sticky="ew", padx=10, pady=(0, 10))
        
        # Status text
        self.status_text = ctk.CTkLabel(
            self.status_bar,
            text="Ready",
            font=ctk.CTkFont(size=12)
        )
        self.status_text.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        
        # Time display
        self.time_display = ctk.CTkLabel(
            self.status_bar,
            text="",
            font=ctk.CTkFont(size=12)
        )
        self.time_display.grid(row=0, column=1, padx=10, pady=5, sticky="e")
        
        self.status_bar.grid_columnconfigure(0, weight=1)
    
    def create_dashboard(self):
        """Create dashboard view"""
        self.dashboard = ctk.CTkFrame(self.main_content)
        
        # Dashboard title
        title = ctk.CTkLabel(
            self.dashboard,
            text="SAM Assistant Dashboard",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        title.grid(row=0, column=0, columnspan=3, padx=20, pady=20)
        
        # Stats cards
        self.create_stats_cards()
        
        # Recent activity
        self.create_recent_activity()
        
        # Quick actions
        self.create_quick_actions()
    
    def create_stats_cards(self):
        """Create statistics cards"""
        stats_frame = ctk.CTkFrame(self.dashboard)
        stats_frame.grid(row=1, column=0, columnspan=3, padx=20, pady=10, sticky="ew")
        
        # Configure grid
        for i in range(4):
            stats_frame.grid_columnconfigure(i, weight=1)
        
        # Create stat cards
        self.stat_cards = {}
        
        stat_configs = [
            ("Commands Processed", "commands", "0"),
            ("Uptime", "uptime", "0:00:00"),
            ("Tasks Completed", "tasks", "0"),
            ("Security Level", "security", "Normal")
        ]
        
        for i, (title, key, default_value) in enumerate(stat_configs):
            card = self.create_stat_card(stats_frame, title, default_value)
            card.grid(row=0, column=i, padx=10, pady=10, sticky="ew")
            self.stat_cards[key] = card
    
    def create_stat_card(self, parent, title, value):
        """Create individual stat card"""
        card = ctk.CTkFrame(parent)
        
        title_label = ctk.CTkLabel(
            card,
            text=title,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        title_label.grid(row=0, column=0, padx=20, pady=(15, 5))
        
        value_label = ctk.CTkLabel(
            card,
            text=value,
            font=ctk.CTkFont(size=24)
        )
        value_label.grid(row=1, column=0, padx=20, pady=(5, 15))
        
        # Store value label for updates
        card.value_label = value_label
        
        return card
    
    def create_recent_activity(self):
        """Create recent activity section"""
        activity_frame = ctk.CTkFrame(self.dashboard)
        activity_frame.grid(row=2, column=0, columnspan=2, padx=20, pady=10, sticky="nsew")
        
        title = ctk.CTkLabel(
            activity_frame,
            text="Recent Activity",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title.grid(row=0, column=0, padx=20, pady=15, sticky="w")
        
        # Activity list
        self.activity_list = ctk.CTkScrollableFrame(activity_frame)
        self.activity_list.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")
        
        activity_frame.grid_columnconfigure(0, weight=1)
        activity_frame.grid_rowconfigure(1, weight=1)
    
    def create_quick_actions(self):
        """Create quick actions panel"""
        actions_frame = ctk.CTkFrame(self.dashboard)
        actions_frame.grid(row=2, column=2, padx=20, pady=10, sticky="nsew")
        
        title = ctk.CTkLabel(
            actions_frame,
            text="Quick Actions",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title.grid(row=0, column=0, padx=20, pady=15)
        
        # Quick action buttons
        quick_actions = [
            ("Start Voice Control", self.quick_start_voice),
            ("Take Screenshot", self.quick_screenshot),
            ("Check Weather", self.quick_weather),
            ("Play Music", self.quick_play_music),
            ("Set Reminder", self.quick_set_reminder)
        ]
        
        for i, (text, command) in enumerate(quick_actions):
            btn = ctk.CTkButton(
                actions_frame,
                text=text,
                command=command,
                width=180
            )
            btn.grid(row=i+1, column=0, padx=20, pady=5)
    
    def create_chat_interface(self):
        """Create chat interface"""
        self.chat_interface = ctk.CTkFrame(self.main_content)
        
        # Chat title
        title = ctk.CTkLabel(
            self.chat_interface,
            text="Chat with SAM",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.grid(row=0, column=0, padx=20, pady=20)
        
        # Chat display
        self.chat_display = ctk.CTkScrollableFrame(self.chat_interface)
        self.chat_display.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        
        # Chat input
        input_frame = ctk.CTkFrame(self.chat_interface)
        input_frame.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        
        self.chat_input = ctk.CTkEntry(
            input_frame,
            placeholder_text="Type your message here...",
            font=ctk.CTkFont(size=14)
        )
        self.chat_input.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        
        send_btn = ctk.CTkButton(
            input_frame,
            text="Send",
            command=self.send_chat_message,
            width=80
        )
        send_btn.grid(row=0, column=1, padx=10, pady=10)
        
        # Configure grid
        self.chat_interface.grid_columnconfigure(0, weight=1)
        self.chat_interface.grid_rowconfigure(1, weight=1)
        input_frame.grid_columnconfigure(0, weight=1)
        
        # Bind Enter key
        self.chat_input.bind("<Return>", lambda e: self.send_chat_message())
    
    def create_voice_control_view(self):
        """Create voice control view"""
        self.voice_control_view = ctk.CTkFrame(self.main_content)
        
        # Title
        title = ctk.CTkLabel(
            self.voice_control_view,
            text="Voice Control",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.grid(row=0, column=0, columnspan=2, padx=20, pady=20)
        
        # Voice status
        self.voice_status_frame = ctk.CTkFrame(self.voice_control_view)
        self.voice_status_frame.grid(row=1, column=0, columnspan=2, padx=20, pady=10, sticky="ew")
        
        # Voice commands list
        commands_frame = ctk.CTkFrame(self.voice_control_view)
        commands_frame.grid(row=2, column=0, padx=20, pady=10, sticky="nsew")
        
        commands_title = ctk.CTkLabel(
            commands_frame,
            text="Available Commands",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        commands_title.grid(row=0, column=0, padx=20, pady=15)
        
        self.commands_list = ctk.CTkScrollableFrame(commands_frame)
        self.commands_list.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")
        
        # Voice settings
        settings_frame = ctk.CTkFrame(self.voice_control_view)
        settings_frame.grid(row=2, column=1, padx=20, pady=10, sticky="nsew")
        
        settings_title = ctk.CTkLabel(
            settings_frame,
            text="Voice Settings",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        settings_title.grid(row=0, column=0, padx=20, pady=15)
        
        # Configure grid
        self.voice_control_view.grid_columnconfigure(0, weight=1)
        self.voice_control_view.grid_columnconfigure(1, weight=1)
        self.voice_control_view.grid_rowconfigure(2, weight=1)
        commands_frame.grid_columnconfigure(0, weight=1)
        commands_frame.grid_rowconfigure(1, weight=1)
    
    def create_computer_vision_view(self):
        """Create computer vision view"""
        self.computer_vision_view = ctk.CTkFrame(self.main_content)
        
        # Title
        title = ctk.CTkLabel(
            self.computer_vision_view,
            text="Computer Vision",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.grid(row=0, column=0, columnspan=2, padx=20, pady=20)
        
        # Camera feed
        self.camera_frame = ctk.CTkFrame(self.computer_vision_view)
        self.camera_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        
        # Camera label
        self.camera_label = ctk.CTkLabel(
            self.camera_frame,
            text="Camera Feed",
            font=ctk.CTkFont(size=16)
        )
        self.camera_label.grid(row=0, column=0, padx=20, pady=20)
        
        # Detection info
        detection_frame = ctk.CTkFrame(self.computer_vision_view)
        detection_frame.grid(row=1, column=1, padx=20, pady=10, sticky="nsew")
        
        detection_title = ctk.CTkLabel(
            detection_frame,
            text="Detection Info",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        detection_title.grid(row=0, column=0, padx=20, pady=15)
        
        self.detection_info = ctk.CTkScrollableFrame(detection_frame)
        self.detection_info.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")
        
        # Configure grid
        self.computer_vision_view.grid_columnconfigure(0, weight=2)
        self.computer_vision_view.grid_columnconfigure(1, weight=1)
        self.computer_vision_view.grid_rowconfigure(1, weight=1)
        detection_frame.grid_columnconfigure(0, weight=1)
        detection_frame.grid_rowconfigure(1, weight=1)
    
    def create_smart_home_view(self):
        """Create smart home view"""
        self.smart_home_view = ctk.CTkFrame(self.main_content)
        
        # Title
        title = ctk.CTkLabel(
            self.smart_home_view,
            text="Smart Home Control",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.grid(row=0, column=0, columnspan=3, padx=20, pady=20)
        
        # Device grid will be populated dynamically
        self.devices_frame = ctk.CTkScrollableFrame(self.smart_home_view)
        self.devices_frame.grid(row=1, column=0, columnspan=3, padx=20, pady=10, sticky="nsew")
        
        # Configure grid
        self.smart_home_view.grid_columnconfigure(0, weight=1)
        self.smart_home_view.grid_columnconfigure(1, weight=1)
        self.smart_home_view.grid_columnconfigure(2, weight=1)
        self.smart_home_view.grid_rowconfigure(1, weight=1)
    
    def create_productivity_view(self):
        """Create productivity view"""
        self.productivity_view = ctk.CTkFrame(self.main_content)
        
        # Title
        title = ctk.CTkLabel(
            self.productivity_view,
            text="Productivity Dashboard",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.grid(row=0, column=0, columnspan=2, padx=20, pady=20)
        
        # Tasks section
        tasks_frame = ctk.CTkFrame(self.productivity_view)
        tasks_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        
        tasks_title = ctk.CTkLabel(
            tasks_frame,
            text="Tasks",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        tasks_title.grid(row=0, column=0, padx=20, pady=15)
        
        self.tasks_list = ctk.CTkScrollableFrame(tasks_frame)
        self.tasks_list.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")
        
        # Calendar section
        calendar_frame = ctk.CTkFrame(self.productivity_view)
        calendar_frame.grid(row=1, column=1, padx=20, pady=10, sticky="nsew")
        
        calendar_title = ctk.CTkLabel(
            calendar_frame,
            text="Calendar",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        calendar_title.grid(row=0, column=0, padx=20, pady=15)
        
        self.calendar_display = ctk.CTkScrollableFrame(calendar_frame)
        self.calendar_display.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")
        
        # Configure grid
        self.productivity_view.grid_columnconfigure(0, weight=1)
        self.productivity_view.grid_columnconfigure(1, weight=1)
        self.productivity_view.grid_rowconfigure(1, weight=1)
        tasks_frame.grid_columnconfigure(0, weight=1)
        tasks_frame.grid_rowconfigure(1, weight=1)
        calendar_frame.grid_columnconfigure(0, weight=1)
        calendar_frame.grid_rowconfigure(1, weight=1)
    
    def create_entertainment_view(self):
        """Create entertainment view"""
        self.entertainment_view = ctk.CTkFrame(self.main_content)
        
        # Title
        title = ctk.CTkLabel(
            self.entertainment_view,
            text="Entertainment Center",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.grid(row=0, column=0, columnspan=2, padx=20, pady=20)
        
        # Music player
        music_frame = ctk.CTkFrame(self.entertainment_view)
        music_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        
        music_title = ctk.CTkLabel(
            music_frame,
            text="Music Player",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        music_title.grid(row=0, column=0, padx=20, pady=15)
        
        # News and weather
        info_frame = ctk.CTkFrame(self.entertainment_view)
        info_frame.grid(row=1, column=1, padx=20, pady=10, sticky="nsew")
        
        info_title = ctk.CTkLabel(
            info_frame,
            text="News & Weather",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        info_title.grid(row=0, column=0, padx=20, pady=15)
        
        # Configure grid
        self.entertainment_view.grid_columnconfigure(0, weight=1)
        self.entertainment_view.grid_columnconfigure(1, weight=1)
        self.entertainment_view.grid_rowconfigure(1, weight=1)
    
    def create_health_wellness_view(self):
        """Create health and wellness view"""
        self.health_wellness_view = ctk.CTkFrame(self.main_content)
        
        # Title
        title = ctk.CTkLabel(
            self.health_wellness_view,
            text="Health & Wellness",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.grid(row=0, column=0, columnspan=2, padx=20, pady=20)
        
        # Fitness tracking
        fitness_frame = ctk.CTkFrame(self.health_wellness_view)
        fitness_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        
        fitness_title = ctk.CTkLabel(
            fitness_frame,
            text="Fitness Tracking",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        fitness_title.grid(row=0, column=0, padx=20, pady=15)
        
        # Health metrics
        health_frame = ctk.CTkFrame(self.health_wellness_view)
        health_frame.grid(row=1, column=1, padx=20, pady=10, sticky="nsew")
        
        health_title = ctk.CTkLabel(
            health_frame,
            text="Health Metrics",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        health_title.grid(row=0, column=0, padx=20, pady=15)
        
        # Configure grid
        self.health_wellness_view.grid_columnconfigure(0, weight=1)
        self.health_wellness_view.grid_columnconfigure(1, weight=1)
        self.health_wellness_view.grid_rowconfigure(1, weight=1)
    
    def create_security_view(self):
        """Create security view"""
        self.security_view = ctk.CTkFrame(self.main_content)
        
        # Title
        title = ctk.CTkLabel(
            self.security_view,
            text="Security Center",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.grid(row=0, column=0, columnspan=2, padx=20, pady=20)
        
        # Security status
        status_frame = ctk.CTkFrame(self.security_view)
        status_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        
        status_title = ctk.CTkLabel(
            status_frame,
            text="Security Status",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        status_title.grid(row=0, column=0, padx=20, pady=15)
        
        # Security logs
        logs_frame = ctk.CTkFrame(self.security_view)
        logs_frame.grid(row=1, column=1, padx=20, pady=10, sticky="nsew")
        
        logs_title = ctk.CTkLabel(
            logs_frame,
            text="Security Logs",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        logs_title.grid(row=0, column=0, padx=20, pady=15)
        
        self.security_logs = ctk.CTkScrollableFrame(logs_frame)
        self.security_logs.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")
        
        # Configure grid
        self.security_view.grid_columnconfigure(0, weight=1)
        self.security_view.grid_columnconfigure(1, weight=1)
        self.security_view.grid_rowconfigure(1, weight=1)
        logs_frame.grid_columnconfigure(0, weight=1)
        logs_frame.grid_rowconfigure(1, weight=1)
    
    def setup_event_handlers(self):
        """Setup event handlers"""
        # Register with assistant events
        self.assistant.register_event_handler("assistant_started", self.on_assistant_started)
        self.assistant.register_event_handler("assistant_stopped", self.on_assistant_stopped)
        self.assistant.register_event_handler("voice_command", self.on_voice_command)
        self.assistant.register_event_handler("notification", self.on_notification)
        
        # Window close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def start_ui_updates(self):
        """Start UI update loop"""
        self.update_ui()
    
    def update_ui(self):
        """Update UI elements"""
        try:
            # Update status indicators
            self.update_status_indicators()
            
            # Update time display
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.time_display.configure(text=current_time)
            
            # Update dashboard stats
            if self.current_view == "dashboard":
                self.update_dashboard_stats()
            
            # Update camera feed
            if self.current_view == "vision":
                self.update_camera_feed()
            
        except Exception as e:
            self.logger.error(f"Error updating UI: {e}")
        
        # Schedule next update
        self.root.after(1000, self.update_ui)
    
    def update_status_indicators(self):
        """Update status indicators"""
        try:
            # Update listening indicator
            if hasattr(self.assistant, 'voice_controller'):
                is_listening = self.assistant.voice_controller.is_listening
                status = "ON" if is_listening else "OFF"
                color = "green" if is_listening else "gray"
                self.listening_indicator.configure(text=f"🎤 Listening: {status}")
            
            # Update speaking indicator
            is_speaking = self.assistant.state.is_speaking
            status = "ON" if is_speaking else "OFF"
            self.speaking_indicator.configure(text=f"🔊 Speaking: {status}")
            
            # Update security indicator
            if hasattr(self.assistant, 'security_controller'):
                security_level = self.assistant.security_controller.security_level.title()
                self.security_indicator.configure(text=f"🔒 Security: {security_level}")
            
        except Exception as e:
            self.logger.error(f"Error updating status indicators: {e}")
    
    def update_dashboard_stats(self):
        """Update dashboard statistics"""
        try:
            status = self.assistant.get_status()
            
            # Update stat cards
            if "commands" in self.stat_cards:
                commands_count = status.get("metrics", {}).get("commands_processed", 0)
                self.stat_cards["commands"].value_label.configure(text=str(commands_count))
            
            if "uptime" in self.stat_cards:
                uptime_seconds = status.get("uptime", 0)
                hours = int(uptime_seconds // 3600)
                minutes = int((uptime_seconds % 3600) // 60)
                seconds = int(uptime_seconds % 60)
                uptime_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
                self.stat_cards["uptime"].value_label.configure(text=uptime_str)
            
        except Exception as e:
            self.logger.error(f"Error updating dashboard stats: {e}")
    
    def update_camera_feed(self):
        """Update camera feed display"""
        try:
            if hasattr(self.assistant, 'computer_vision') and self.assistant.computer_vision.current_frame is not None:
                frame = self.assistant.computer_vision.current_frame
                
                # Resize frame for display
                height, width = frame.shape[:2]
                display_width = 640
                display_height = int(height * (display_width / width))
                
                frame_resized = cv2.resize(frame, (display_width, display_height))
                frame_rgb = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB)
                
                # Convert to PIL Image
                pil_image = Image.fromarray(frame_rgb)
                photo = ImageTk.PhotoImage(pil_image)
                
                # Update camera label
                self.camera_label.configure(image=photo, text="")
                self.camera_label.image = photo  # Keep a reference
            
        except Exception as e:
            self.logger.error(f"Error updating camera feed: {e}")
    
    # Navigation methods
    def show_view(self, view_name):
        """Show specific view"""
        # Hide all views
        for view in [self.dashboard, self.chat_interface, self.voice_control_view,
                    self.computer_vision_view, self.smart_home_view, self.productivity_view,
                    self.entertainment_view, self.health_wellness_view, self.security_view]:
            if view:
                view.grid_remove()
        
        # Show selected view
        view_map = {
            "dashboard": self.dashboard,
            "chat": self.chat_interface,
            "voice": self.voice_control_view,
            "vision": self.computer_vision_view,
            "smart_home": self.smart_home_view,
            "productivity": self.productivity_view,
            "entertainment": self.entertainment_view,
            "health": self.health_wellness_view,
            "security": self.security_view
        }
        
        if view_name in view_map and view_map[view_name]:
            view_map[view_name].grid(row=0, column=0, sticky="nsew")
            self.current_view = view_name
            
            # Update navigation button states
            for key, btn in self.nav_buttons.items():
                if key == view_name:
                    btn.configure(fg_color=("gray75", "gray25"))
                else:
                    btn.configure(fg_color=("gray85", "gray15"))
    
    def show_dashboard(self):
        self.show_view("dashboard")
    
    def show_chat(self):
        self.show_view("chat")
    
    def show_voice_control(self):
        self.show_view("voice")
    
    def show_computer_vision(self):
        self.show_view("vision")
    
    def show_smart_home(self):
        self.show_view("smart_home")
    
    def show_productivity(self):
        self.show_view("productivity")
    
    def show_entertainment(self):
        self.show_view("entertainment")
    
    def show_health_wellness(self):
        self.show_view("health")
    
    def show_security(self):
        self.show_view("security")
    
    def show_settings(self):
        """Show settings dialog"""
        settings_window = SettingsWindow(self, self.assistant)
    
    # Control methods
    def toggle_voice_control(self):
        """Toggle voice control"""
        try:
            if hasattr(self.assistant, 'voice_controller'):
                if self.assistant.voice_controller.is_listening:
                    self.assistant.voice_controller.stop_listening()
                else:
                    asyncio.create_task(self.assistant.voice_controller.start_listening())
        except Exception as e:
            self.logger.error(f"Error toggling voice control: {e}")
    
    def toggle_privacy_mode(self):
        """Toggle privacy mode"""
        try:
            if hasattr(self.assistant, 'security_controller'):
                if self.assistant.security_controller.privacy_mode:
                    self.assistant.security_controller.disable_privacy_mode()
                else:
                    self.assistant.security_controller.enable_privacy_mode()
        except Exception as e:
            self.logger.error(f"Error toggling privacy mode: {e}")
    
    def toggle_camera(self):
        """Toggle camera"""
        try:
            if hasattr(self.assistant, 'computer_vision'):
                if self.assistant.computer_vision.camera_active:
                    self.assistant.computer_vision.stop_camera()
                else:
                    self.assistant.computer_vision.start_camera()
        except Exception as e:
            self.logger.error(f"Error toggling camera: {e}")
    
    # Chat methods
    def send_chat_message(self):
        """Send chat message"""
        try:
            message = self.chat_input.get().strip()
            if not message:
                return
            
            # Clear input
            self.chat_input.delete(0, tk.END)
            
            # Add user message to chat
            self.add_chat_message("You", message, "user")
            
            # Process message (placeholder)
            response = f"I received your message: {message}"
            self.add_chat_message("SAM", response, "assistant")
            
        except Exception as e:
            self.logger.error(f"Error sending chat message: {e}")
    
    def add_chat_message(self, sender, message, message_type):
        """Add message to chat display"""
        try:
            message_frame = ctk.CTkFrame(self.chat_display)
            message_frame.grid(sticky="ew", padx=10, pady=5)
            
            # Sender label
            sender_label = ctk.CTkLabel(
                message_frame,
                text=f"{sender}:",
                font=ctk.CTkFont(size=12, weight="bold")
            )
            sender_label.grid(row=0, column=0, sticky="w", padx=10, pady=(10, 5))
            
            # Message label
            message_label = ctk.CTkLabel(
                message_frame,
                text=message,
                font=ctk.CTkFont(size=12),
                wraplength=500,
                justify="left"
            )
            message_label.grid(row=1, column=0, sticky="w", padx=10, pady=(0, 10))
            
            # Scroll to bottom
            self.chat_display._parent_canvas.yview_moveto(1.0)
            
        except Exception as e:
            self.logger.error(f"Error adding chat message: {e}")
    
    # Quick action methods
    def quick_start_voice(self):
        """Quick start voice control"""
        self.voice_toggle.select()
        self.toggle_voice_control()
    
    def quick_screenshot(self):
        """Quick take screenshot"""
        if hasattr(self.assistant, 'computer_vision'):
            self.assistant.computer_vision.take_screenshot()
            self.update_status("Screenshot taken")
    
    def quick_weather(self):
        """Quick check weather"""
        self.update_status("Checking weather...")
    
    def quick_play_music(self):
        """Quick play music"""
        if hasattr(self.assistant, 'entertainment_controller'):
            self.assistant.entertainment_controller.music_player.play()
            self.update_status("Music started")
    
    def quick_set_reminder(self):
        """Quick set reminder"""
        self.update_status("Reminder feature activated")
    
    # Event handlers
    def on_assistant_started(self, data):
        """Handle assistant started event"""
        self.update_status("Assistant started")
    
    def on_assistant_stopped(self, data):
        """Handle assistant stopped event"""
        self.update_status("Assistant stopped")
    
    def on_voice_command(self, data):
        """Handle voice command event"""
        command = data.get("command", "Unknown command")
        self.update_status(f"Voice command: {command}")
    
    def on_notification(self, data):
        """Handle notification event"""
        message = data.get("message", "Notification")
        self.update_status(message)
    
    def update_status(self, message):
        """Update status bar message"""
        self.status_text.configure(text=message)
        
        # Clear status after 5 seconds
        self.root.after(5000, lambda: self.status_text.configure(text="Ready"))
    
    def on_closing(self):
        """Handle window closing"""
        try:
            # Stop assistant
            asyncio.create_task(self.assistant.stop())
            
            # Destroy window
            self.root.destroy()
            
        except Exception as e:
            self.logger.error(f"Error during closing: {e}")
            self.root.destroy()
    
    def run(self):
        """Run the main window"""
        self.root.mainloop()


class SettingsWindow:
    """Settings dialog window"""
    
    def __init__(self, parent, assistant):
        self.parent = parent  # MainWindow instance
        self.assistant = assistant
        
        # Create settings window
        self.window = ctk.CTkToplevel(parent.root)
        self.window.title("Settings")
        self.window.geometry("600x500")
        self.window.transient(parent)
        self.window.grab_set()
        
        self.create_settings_ui()
    
    def create_settings_ui(self):
        """Create settings UI"""
        # Title
        title = ctk.CTkLabel(
            self.window,
            text="SAM Assistant Settings",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title.grid(row=0, column=0, columnspan=2, padx=20, pady=20)
        
        # Settings tabs
        self.tabview = ctk.CTkTabview(self.window)
        self.tabview.grid(row=1, column=0, columnspan=2, padx=20, pady=10, sticky="nsew")
        
        # Create tabs
        self.tabview.add("General")
        self.tabview.add("Voice")
        self.tabview.add("Security")
        self.tabview.add("Appearance")
        self.tabview.add("AI")
        
        # Populate tabs
        self.create_general_settings()
        self.create_voice_settings()
        self.create_security_settings()
        self.create_appearance_settings()
        self.create_ai_settings()
        
        # Buttons
        button_frame = ctk.CTkFrame(self.window)
        button_frame.grid(row=2, column=0, columnspan=2, padx=20, pady=20, sticky="ew")
        
        save_btn = ctk.CTkButton(
            button_frame,
            text="Save",
            command=self.save_settings
        )
        save_btn.grid(row=0, column=0, padx=10, pady=10)
        
        cancel_btn = ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=self.window.destroy
        )
        cancel_btn.grid(row=0, column=1, padx=10, pady=10)
        
        # Configure grid
        self.window.grid_columnconfigure(0, weight=1)
        self.window.grid_rowconfigure(1, weight=1)
    
    def create_general_settings(self):
        """Create general settings"""
        general_frame = self.tabview.tab("General")
        
        # Auto-start setting
        auto_start = ctk.CTkCheckBox(
            general_frame,
            text="Start with system"
        )
        auto_start.grid(row=0, column=0, padx=20, pady=10, sticky="w")
        
        # Logging level
        logging_label = ctk.CTkLabel(general_frame, text="Logging Level:")
        logging_label.grid(row=1, column=0, padx=20, pady=(20, 5), sticky="w")
        
        logging_combo = ctk.CTkComboBox(
            general_frame,
            values=["DEBUG", "INFO", "WARNING", "ERROR"]
        )
        logging_combo.grid(row=2, column=0, padx=20, pady=5, sticky="w")
    
    def create_voice_settings(self):
        """Create voice settings"""
        voice_frame = self.tabview.tab("Voice")
        
        # Wake word
        wake_word_label = ctk.CTkLabel(voice_frame, text="Wake Word:")
        wake_word_label.grid(row=0, column=0, padx=20, pady=(20, 5), sticky="w")
        
        wake_word_entry = ctk.CTkEntry(voice_frame, placeholder_text="sam")
        wake_word_entry.grid(row=1, column=0, padx=20, pady=5, sticky="ew")
        
        # Language
        language_label = ctk.CTkLabel(voice_frame, text="Language:")
        language_label.grid(row=2, column=0, padx=20, pady=(20, 5), sticky="w")
        
        language_combo = ctk.CTkComboBox(
            voice_frame,
            values=["en-US", "en-GB", "es-ES", "fr-FR", "de-DE"]
        )
        language_combo.grid(row=3, column=0, padx=20, pady=5, sticky="ew")
        
        # TTS Rate
        tts_rate_label = ctk.CTkLabel(voice_frame, text="Speech Rate:")
        tts_rate_label.grid(row=4, column=0, padx=20, pady=(20, 5), sticky="w")
        
        tts_rate_slider = ctk.CTkSlider(voice_frame, from_=100, to=300)
        tts_rate_slider.grid(row=5, column=0, padx=20, pady=5, sticky="ew")
        
        voice_frame.grid_columnconfigure(0, weight=1)
    
    def create_security_settings(self):
        """Create security settings"""
        security_frame = self.tabview.tab("Security")
        
        # Biometric authentication
        biometric_check = ctk.CTkCheckBox(
            security_frame,
            text="Enable biometric authentication"
        )
        biometric_check.grid(row=0, column=0, padx=20, pady=10, sticky="w")
        
        # Session timeout
        timeout_label = ctk.CTkLabel(security_frame, text="Session Timeout (minutes):")
        timeout_label.grid(row=1, column=0, padx=20, pady=(20, 5), sticky="w")
        
        timeout_entry = ctk.CTkEntry(security_frame, placeholder_text="30")
        timeout_entry.grid(row=2, column=0, padx=20, pady=5, sticky="ew")
        
        # Auto-lock
        auto_lock_check = ctk.CTkCheckBox(
            security_frame,
            text="Auto-lock after inactivity"
        )
        auto_lock_check.grid(row=3, column=0, padx=20, pady=10, sticky="w")
        
        security_frame.grid_columnconfigure(0, weight=1)
    
    def create_appearance_settings(self):
        """Create appearance settings"""
        appearance_frame = self.tabview.tab("Appearance")
        
        # Theme
        theme_label = ctk.CTkLabel(appearance_frame, text="Theme:")
        theme_label.grid(row=0, column=0, padx=20, pady=(20, 5), sticky="w")
        
        theme_combo = ctk.CTkComboBox(
            appearance_frame,
            values=["dark", "light", "system"]
        )
        theme_combo.grid(row=1, column=0, padx=20, pady=5, sticky="ew")
        
        # Color theme
        color_label = ctk.CTkLabel(appearance_frame, text="Color Theme:")
        color_label.grid(row=2, column=0, padx=20, pady=(20, 5), sticky="w")
        
        color_combo = ctk.CTkComboBox(
            appearance_frame,
            values=["blue", "green", "dark-blue"]
        )
        color_combo.grid(row=3, column=0, padx=20, pady=5, sticky="ew")
        
        # Font size
        font_size_label = ctk.CTkLabel(appearance_frame, text="Font Size:")
        font_size_label.grid(row=4, column=0, padx=20, pady=(20, 5), sticky="w")
        
        font_size_slider = ctk.CTkSlider(appearance_frame, from_=10, to=16)
        font_size_slider.grid(row=5, column=0, padx=20, pady=5, sticky="ew")
        
        appearance_frame.grid_columnconfigure(0, weight=1)

    def create_ai_settings(self):
        """Create AI/API settings, including a field to set the Gemini API key"""
        ai_frame = self.tabview.tab("AI")

        # Provider info
        provider_label = ctk.CTkLabel(ai_frame, text="LLM Provider: Gemini")
        provider_label.grid(row=0, column=0, padx=20, pady=(20, 5), sticky="w")

        # Gemini API Key field
        key_label = ctk.CTkLabel(ai_frame, text="Gemini API Key:")
        key_label.grid(row=1, column=0, padx=20, pady=(10, 5), sticky="w")

        self.gemini_key_entry = ctk.CTkEntry(ai_frame, placeholder_text="Enter your Gemini API key")
        self.gemini_key_entry.grid(row=2, column=0, padx=20, pady=5, sticky="ew")

        # Pre-fill with current value if present (masked)
        try:
            current_key = API_KEYS.get("gemini")
            if current_key and len(current_key) > 8:
                masked = current_key[:4] + "…" + current_key[-4:]
                # Show masked value as placeholder
                self.gemini_key_entry.configure(placeholder_text=f"Current: {masked}")
        except Exception:
            pass

        # Save key button
        save_key_btn = ctk.CTkButton(ai_frame, text="Save API Key", command=self.save_api_key)
        save_key_btn.grid(row=3, column=0, padx=20, pady=10, sticky="w")

        # Info text
        info_text = ctk.CTkLabel(
            ai_frame,
            text="Your key is stored locally in config/local_settings.py (not committed).",
            font=ctk.CTkFont(size=11)
        )
        info_text.grid(row=4, column=0, padx=20, pady=(0, 10), sticky="w")

        ai_frame.grid_columnconfigure(0, weight=1)
    
    def save_settings(self):
        """Save settings"""
        # Save general settings (placeholder)
        self.window.destroy()

    def save_api_key(self):
        """Handle saving the Gemini API key from UI"""
        try:
            key = (self.gemini_key_entry.get() or "").strip()
            if not key:
                # No key entered; nothing to do
                return
            ok = False
            if hasattr(self.assistant, "set_api_key"):
                ok = self.assistant.set_api_key("gemini", key, persist=True)
            if ok:
                # Try to reinitialize AI provider if method exists
                try:
                    if hasattr(self.assistant, "initialize_ai"):
                        self.assistant.initialize_ai()
                except Exception:
                    pass
                # Update status in the main window
                try:
                    if hasattr(self.parent, "update_status"):
                        self.parent.update_status("Gemini API key saved. AI is ready.")
                except Exception:
                    pass
                # Close settings window
                self.window.destroy()
            else:
                try:
                    if hasattr(self.parent, "update_status"):
                        self.parent.update_status("Failed to save API key. Check logs.")
                except Exception:
                    pass
        except Exception as e:
            logging.error(f"Error saving API key: {e}")