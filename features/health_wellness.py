"""
Enhanced SAM AI Assistant - Health & Wellness Module
"""
import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import threading
import sqlite3
import numpy as np
import cv2

from core.base_assistant import BaseAssistant
from config.settings import DATA_DIR

class HealthWellnessController:
    """Comprehensive health and wellness management system"""
    
    def __init__(self, assistant: BaseAssistant):
        self.assistant = assistant
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Initialize components
        self.fitness_tracker = FitnessTracker(self)
        self.meditation_guide = MeditationGuide(self)
        self.health_monitor = HealthMonitor(self)
        self.sleep_tracker = SleepTracker(self)
        self.posture_monitor = PostureMonitor(self)
        self.nutrition_tracker = NutritionTracker(self)
        self.mental_health_assistant = MentalHealthAssistant(self)
        
        # Database setup
        self.setup_database()
        
        # Register voice commands
        self.register_voice_commands()
        
        # Start monitoring services
        self.start_monitoring_services()
    
    def setup_database(self):
        """Setup health and wellness database"""
        try:
            self.db_path = DATA_DIR / "health_wellness.db"
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Fitness activities table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS fitness_activities (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    activity_type TEXT NOT NULL,
                    duration INTEGER,
                    calories_burned INTEGER,
                    distance REAL,
                    intensity TEXT,
                    notes TEXT,
                    created_at TEXT
                )
            ''')
            
            # Health metrics table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS health_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    metric_type TEXT NOT NULL,
                    value REAL,
                    unit TEXT,
                    notes TEXT,
                    recorded_at TEXT
                )
            ''')
            
            # Sleep data table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sleep_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sleep_start TEXT,
                    sleep_end TEXT,
                    duration INTEGER,
                    quality_score INTEGER,
                    notes TEXT,
                    created_at TEXT
                )
            ''')
            
            # Meditation sessions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS meditation_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_type TEXT,
                    duration INTEGER,
                    mood_before INTEGER,
                    mood_after INTEGER,
                    notes TEXT,
                    created_at TEXT
                )
            ''')
            
            # Nutrition entries table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS nutrition_entries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    meal_type TEXT,
                    food_item TEXT,
                    calories INTEGER,
                    protein REAL,
                    carbs REAL,
                    fat REAL,
                    fiber REAL,
                    created_at TEXT
                )
            ''')
            
            # Mental health entries table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS mental_health_entries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    mood_score INTEGER,
                    stress_level INTEGER,
                    anxiety_level INTEGER,
                    energy_level INTEGER,
                    notes TEXT,
                    created_at TEXT
                )
            ''')
            
            conn.commit()
            conn.close()
            
            self.logger.info("Health & Wellness database initialized")
            
        except Exception as e:
            self.logger.error(f"Error setting up database: {e}")
    
    def register_voice_commands(self):
        """Register health and wellness voice commands"""
        if hasattr(self.assistant, 'voice_controller'):
            voice = self.assistant.voice_controller
            
            # Fitness commands
            voice.register_command(
                ["start workout", "begin exercise", "start fitness"],
                self.voice_start_workout,
                "Start a workout session"
            )
            
            voice.register_command(
                ["end workout", "finish exercise", "stop workout"],
                self.voice_end_workout,
                "End current workout"
            )
            
            voice.register_command(
                ["log exercise *", "record workout *"],
                self.voice_log_exercise,
                "Log an exercise activity"
            )
            
            # Meditation commands
            voice.register_command(
                ["start meditation", "begin meditation", "meditate"],
                self.voice_start_meditation,
                "Start a meditation session"
            )
            
            voice.register_command(
                ["guided breathing", "breathing exercise"],
                self.voice_guided_breathing,
                "Start guided breathing exercise"
            )
            
            # Health monitoring commands
            voice.register_command(
                ["check posture", "posture check"],
                self.voice_check_posture,
                "Check current posture"
            )
            
            voice.register_command(
                ["record weight *", "log weight *"],
                self.voice_record_weight,
                "Record weight measurement"
            )
            
            voice.register_command(
                ["record blood pressure *", "log blood pressure *"],
                self.voice_record_blood_pressure,
                "Record blood pressure"
            )
            
            # Sleep commands
            voice.register_command(
                ["going to sleep", "bedtime", "sleep time"],
                self.voice_bedtime,
                "Record bedtime"
            )
            
            voice.register_command(
                ["wake up", "good morning", "I'm awake"],
                self.voice_wake_up,
                "Record wake up time"
            )
            
            # Mental health commands
            voice.register_command(
                ["mood check", "how am I feeling", "mental health check"],
                self.voice_mood_check,
                "Check current mood and mental state"
            )
            
            voice.register_command(
                ["stress relief", "I'm stressed", "help with stress"],
                self.voice_stress_relief,
                "Get stress relief suggestions"
            )
            
            # Nutrition commands
            voice.register_command(
                ["log meal *", "record food *", "ate *"],
                self.voice_log_meal,
                "Log a meal or food item"
            )
            
            voice.register_command(
                ["water reminder", "drink water", "hydration reminder"],
                self.voice_water_reminder,
                "Set water drinking reminder"
            )
    
    def start_monitoring_services(self):
        """Start background monitoring services"""
        self.posture_monitor.start_monitoring()
        self.health_monitor.start_monitoring()
    
    # Voice command handlers
    def voice_start_workout(self, text: str):
        """Handle voice start workout command"""
        if self.fitness_tracker.start_workout():
            self.assistant.voice_controller.speak("Workout started. Good luck with your exercise!")
        else:
            self.assistant.voice_controller.speak("Unable to start workout")
    
    def voice_end_workout(self, text: str):
        """Handle voice end workout command"""
        if self.fitness_tracker.end_workout():
            stats = self.fitness_tracker.get_current_session_stats()
            duration = stats.get('duration', 0)
            self.assistant.voice_controller.speak(f"Great workout! You exercised for {duration} minutes.")
        else:
            self.assistant.voice_controller.speak("No active workout to end")
    
    def voice_log_exercise(self, text: str):
        """Handle voice log exercise command"""
        # Extract exercise details from text
        words = text.split()
        if len(words) > 2:
            exercise_type = ' '.join(words[2:])  # Skip "log exercise"
            
            if self.fitness_tracker.log_activity(exercise_type):
                self.assistant.voice_controller.speak(f"Logged {exercise_type} activity")
            else:
                self.assistant.voice_controller.speak("Failed to log exercise")
    
    def voice_start_meditation(self, text: str):
        """Handle voice start meditation command"""
        if self.meditation_guide.start_session():
            self.assistant.voice_controller.speak("Starting meditation session. Find a comfortable position and close your eyes.")
        else:
            self.assistant.voice_controller.speak("Unable to start meditation session")
    
    def voice_guided_breathing(self, text: str):
        """Handle voice guided breathing command"""
        self.meditation_guide.start_breathing_exercise()
        self.assistant.voice_controller.speak("Let's begin a breathing exercise. Breathe in slowly through your nose.")
    
    def voice_check_posture(self, text: str):
        """Handle voice check posture command"""
        posture_status = self.posture_monitor.check_current_posture()
        
        if posture_status['good_posture']:
            self.assistant.voice_controller.speak("Your posture looks good!")
        else:
            self.assistant.voice_controller.speak("Please adjust your posture. Sit up straight and align your shoulders.")
    
    def voice_record_weight(self, text: str):
        """Handle voice record weight command"""
        # Extract weight from text
        words = text.split()
        try:
            weight = float([w for w in words if w.replace('.', '').isdigit()][0])
            
            if self.health_monitor.record_metric('weight', weight, 'lbs'):
                self.assistant.voice_controller.speak(f"Recorded weight: {weight} pounds")
            else:
                self.assistant.voice_controller.speak("Failed to record weight")
        except:
            self.assistant.voice_controller.speak("Please specify your weight in numbers")
    
    def voice_record_blood_pressure(self, text: str):
        """Handle voice record blood pressure command"""
        self.assistant.voice_controller.speak("Blood pressure recording feature activated")
    
    def voice_bedtime(self, text: str):
        """Handle voice bedtime command"""
        if self.sleep_tracker.start_sleep_tracking():
            self.assistant.voice_controller.speak("Good night! Sleep tracking started. Sweet dreams!")
        else:
            self.assistant.voice_controller.speak("Sleep tracking already active")
    
    def voice_wake_up(self, text: str):
        """Handle voice wake up command"""
        if self.sleep_tracker.end_sleep_tracking():
            sleep_stats = self.sleep_tracker.get_last_sleep_stats()
            duration = sleep_stats.get('duration_hours', 0)
            self.assistant.voice_controller.speak(f"Good morning! You slept for {duration:.1f} hours.")
        else:
            self.assistant.voice_controller.speak("Good morning! No sleep tracking was active.")
    
    def voice_mood_check(self, text: str):
        """Handle voice mood check command"""
        self.mental_health_assistant.start_mood_assessment()
        self.assistant.voice_controller.speak("Let's check how you're feeling. On a scale of 1 to 10, how would you rate your mood today?")
    
    def voice_stress_relief(self, text: str):
        """Handle voice stress relief command"""
        suggestions = self.mental_health_assistant.get_stress_relief_suggestions()
        
        if suggestions:
            self.assistant.voice_controller.speak("Here are some stress relief suggestions:")
            for suggestion in suggestions[:3]:  # Top 3 suggestions
                self.assistant.voice_controller.speak(suggestion)
        else:
            self.assistant.voice_controller.speak("Try taking deep breaths and relaxing for a few minutes")
    
    def voice_log_meal(self, text: str):
        """Handle voice log meal command"""
        words = text.split()
        if len(words) > 2:
            food_item = ' '.join(words[2:])  # Skip "log meal"
            
            if self.nutrition_tracker.log_food(food_item):
                self.assistant.voice_controller.speak(f"Logged {food_item} to your nutrition diary")
            else:
                self.assistant.voice_controller.speak("Failed to log meal")
    
    def voice_water_reminder(self, text: str):
        """Handle voice water reminder command"""
        self.nutrition_tracker.set_water_reminder()
        self.assistant.voice_controller.speak("Water reminder set. I'll remind you to stay hydrated!")
    
    def get_health_wellness_stats(self) -> Dict:
        """Get health and wellness statistics"""
        return {
            'fitness': {
                'active_workout': self.fitness_tracker.is_workout_active(),
                'today_activities': self.fitness_tracker.get_today_activity_count(),
                'weekly_goal_progress': self.fitness_tracker.get_weekly_progress()
            },
            'sleep': {
                'tracking_active': self.sleep_tracker.is_tracking(),
                'last_sleep_duration': self.sleep_tracker.get_last_sleep_duration(),
                'average_sleep_quality': self.sleep_tracker.get_average_sleep_quality()
            },
            'meditation': {
                'sessions_this_week': self.meditation_guide.get_weekly_session_count(),
                'total_meditation_time': self.meditation_guide.get_total_meditation_time()
            },
            'posture': {
                'monitoring_active': self.posture_monitor.is_monitoring(),
                'posture_score': self.posture_monitor.get_current_score()
            },
            'mental_health': {
                'average_mood': self.mental_health_assistant.get_average_mood(),
                'stress_level': self.mental_health_assistant.get_current_stress_level()
            }
        }


class FitnessTracker:
    """Fitness activity tracking and management"""
    
    def __init__(self, health_controller):
        self.controller = health_controller
        self.logger = logging.getLogger(self.__class__.__name__)
        
        self.current_workout = None
        self.workout_start_time = None
        self.daily_goals = {
            'steps': 10000,
            'calories': 500,
            'exercise_minutes': 30
        }
        
        self.activity_types = [
            'walking', 'running', 'cycling', 'swimming', 'weightlifting',
            'yoga', 'pilates', 'dancing', 'hiking', 'basketball',
            'tennis', 'soccer', 'boxing', 'rowing', 'climbing'
        ]
    
    def start_workout(self, activity_type: str = "general") -> bool:
        """Start a workout session"""
        try:
            if self.current_workout:
                self.end_workout()  # End previous workout
            
            self.current_workout = {
                'activity_type': activity_type,
                'start_time': datetime.now(),
                'calories_burned': 0,
                'distance': 0.0
            }
            
            self.workout_start_time = datetime.now()
            self.logger.info(f"Started workout: {activity_type}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error starting workout: {e}")
            return False
    
    def end_workout(self) -> bool:
        """End current workout session"""
        try:
            if not self.current_workout:
                return False
            
            end_time = datetime.now()
            duration = (end_time - self.current_workout['start_time']).total_seconds() / 60  # minutes
            
            # Save workout to database
            conn = sqlite3.connect(self.controller.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO fitness_activities (activity_type, duration, calories_burned, distance, created_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                self.current_workout['activity_type'],
                int(duration),
                self.current_workout['calories_burned'],
                self.current_workout['distance'],
                datetime.now().isoformat()
            ))
            
            conn.commit()
            conn.close()
            
            self.logger.info(f"Ended workout: {self.current_workout['activity_type']}, Duration: {duration:.1f} minutes")
            self.current_workout = None
            self.workout_start_time = None
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error ending workout: {e}")
            return False
    
    def log_activity(self, activity_type: str, duration: int = 30, 
                    calories: int = None, distance: float = None) -> bool:
        """Log a completed activity"""
        try:
            if calories is None:
                calories = self._estimate_calories(activity_type, duration)
            
            conn = sqlite3.connect(self.controller.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO fitness_activities (activity_type, duration, calories_burned, distance, created_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (activity_type, duration, calories, distance or 0.0, datetime.now().isoformat()))
            
            conn.commit()
            conn.close()
            
            self.logger.info(f"Logged activity: {activity_type}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error logging activity: {e}")
            return False
    
    def _estimate_calories(self, activity_type: str, duration: int) -> int:
        """Estimate calories burned for activity"""
        # Simplified calorie estimation (calories per minute)
        calorie_rates = {
            'walking': 4,
            'running': 10,
            'cycling': 8,
            'swimming': 12,
            'weightlifting': 6,
            'yoga': 3,
            'dancing': 5,
            'hiking': 7
        }
        
        rate = calorie_rates.get(activity_type.lower(), 5)  # Default 5 cal/min
        return rate * duration
    
    def is_workout_active(self) -> bool:
        """Check if workout is currently active"""
        return self.current_workout is not None
    
    def get_current_session_stats(self) -> Dict:
        """Get current workout session statistics"""
        if not self.current_workout:
            return {}
        
        duration = (datetime.now() - self.current_workout['start_time']).total_seconds() / 60
        
        return {
            'activity_type': self.current_workout['activity_type'],
            'duration': int(duration),
            'calories_burned': self.current_workout['calories_burned'],
            'distance': self.current_workout['distance']
        }
    
    def get_today_activity_count(self) -> int:
        """Get count of activities today"""
        try:
            today = datetime.now().date().isoformat()
            
            conn = sqlite3.connect(self.controller.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT COUNT(*) FROM fitness_activities 
                WHERE DATE(created_at) = ?
            ''', (today,))
            
            count = cursor.fetchone()[0]
            conn.close()
            
            return count
            
        except Exception as e:
            self.logger.error(f"Error getting today's activity count: {e}")
            return 0
    
    def get_weekly_progress(self) -> Dict:
        """Get weekly fitness progress"""
        try:
            week_start = (datetime.now() - timedelta(days=7)).isoformat()
            
            conn = sqlite3.connect(self.controller.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT SUM(duration), SUM(calories_burned) FROM fitness_activities 
                WHERE created_at >= ?
            ''', (week_start,))
            
            result = cursor.fetchone()
            total_minutes = result[0] or 0
            total_calories = result[1] or 0
            
            conn.close()
            
            return {
                'total_minutes': total_minutes,
                'total_calories': total_calories,
                'goal_progress': {
                    'exercise_minutes': min(100, (total_minutes / (self.daily_goals['exercise_minutes'] * 7)) * 100),
                    'calories': min(100, (total_calories / (self.daily_goals['calories'] * 7)) * 100)
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error getting weekly progress: {e}")
            return {}


class MeditationGuide:
    """Meditation and mindfulness guide"""
    
    def __init__(self, health_controller):
        self.controller = health_controller
        self.logger = logging.getLogger(self.__class__.__name__)
        
        self.current_session = None
        self.meditation_types = [
            'mindfulness', 'breathing', 'body_scan', 'loving_kindness',
            'concentration', 'walking', 'visualization'
        ]
        
        self.breathing_patterns = {
            'basic': {'inhale': 4, 'hold': 4, 'exhale': 4, 'pause': 2},
            'relaxing': {'inhale': 4, 'hold': 7, 'exhale': 8, 'pause': 0},
            'energizing': {'inhale': 6, 'hold': 2, 'exhale': 4, 'pause': 2}
        }
    
    def start_session(self, session_type: str = "mindfulness", duration: int = 10) -> bool:
        """Start a meditation session"""
        try:
            self.current_session = {
                'type': session_type,
                'duration': duration,
                'start_time': datetime.now(),
                'mood_before': None,
                'mood_after': None
            }
            
            self.logger.info(f"Started meditation session: {session_type}")
            
            # Start guided meditation
            threading.Thread(target=self._guide_meditation, args=(session_type, duration), daemon=True).start()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error starting meditation session: {e}")
            return False
    
    def _guide_meditation(self, session_type: str, duration: int):
        """Guide meditation session"""
        try:
            if hasattr(self.controller.assistant, 'voice_controller'):
                voice = self.controller.assistant.voice_controller
                
                if session_type == "mindfulness":
                    voice.speak("Focus on your breath. Notice each inhale and exhale.")
                    time.sleep(30)
                    voice.speak("If your mind wanders, gently bring your attention back to your breath.")
                    time.sleep(duration * 60 - 60)  # Remaining time
                    voice.speak("Slowly open your eyes. Your meditation session is complete.")
                
                elif session_type == "breathing":
                    self._guide_breathing_exercise(duration)
                
                elif session_type == "body_scan":
                    voice.speak("Start by focusing on your toes. Notice any sensations.")
                    time.sleep(duration * 60)
                    voice.speak("Your body scan meditation is complete.")
            
            self._end_session()
            
        except Exception as e:
            self.logger.error(f"Error guiding meditation: {e}")
    
    def start_breathing_exercise(self, pattern: str = "basic", cycles: int = 10):
        """Start guided breathing exercise"""
        try:
            if pattern not in self.breathing_patterns:
                pattern = "basic"
            
            breathing = self.breathing_patterns[pattern]
            
            if hasattr(self.controller.assistant, 'voice_controller'):
                voice = self.controller.assistant.voice_controller
                
                for cycle in range(cycles):
                    voice.speak("Breathe in")
                    time.sleep(breathing['inhale'])
                    
                    if breathing['hold'] > 0:
                        voice.speak("Hold")
                        time.sleep(breathing['hold'])
                    
                    voice.speak("Breathe out")
                    time.sleep(breathing['exhale'])
                    
                    if breathing['pause'] > 0:
                        time.sleep(breathing['pause'])
                
                voice.speak("Breathing exercise complete. Well done!")
            
        except Exception as e:
            self.logger.error(f"Error in breathing exercise: {e}")
    
    def _guide_breathing_exercise(self, duration: int):
        """Guide breathing exercise for specified duration"""
        try:
            if hasattr(self.controller.assistant, 'voice_controller'):
                voice = self.controller.assistant.voice_controller
                
                cycles = duration * 2  # Approximately 2 cycles per minute
                pattern = self.breathing_patterns['basic']
                
                for cycle in range(cycles):
                    voice.speak("Inhale")
                    time.sleep(pattern['inhale'])
                    voice.speak("Exhale")
                    time.sleep(pattern['exhale'])
                
                voice.speak("Breathing meditation complete.")
                
        except Exception as e:
            self.logger.error(f"Error guiding breathing exercise: {e}")
    
    def _end_session(self):
        """End current meditation session"""
        try:
            if not self.current_session:
                return
            
            end_time = datetime.now()
            actual_duration = (end_time - self.current_session['start_time']).total_seconds() / 60
            
            # Save session to database
            conn = sqlite3.connect(self.controller.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO meditation_sessions (session_type, duration, mood_before, mood_after, created_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                self.current_session['type'],
                int(actual_duration),
                self.current_session.get('mood_before'),
                self.current_session.get('mood_after'),
                datetime.now().isoformat()
            ))
            
            conn.commit()
            conn.close()
            
            self.logger.info(f"Completed meditation session: {actual_duration:.1f} minutes")
            self.current_session = None
            
        except Exception as e:
            self.logger.error(f"Error ending meditation session: {e}")
    
    def get_weekly_session_count(self) -> int:
        """Get count of meditation sessions this week"""
        try:
            week_start = (datetime.now() - timedelta(days=7)).isoformat()
            
            conn = sqlite3.connect(self.controller.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT COUNT(*) FROM meditation_sessions 
                WHERE created_at >= ?
            ''', (week_start,))
            
            count = cursor.fetchone()[0]
            conn.close()
            
            return count
            
        except Exception as e:
            self.logger.error(f"Error getting weekly session count: {e}")
            return 0
    
    def get_total_meditation_time(self) -> int:
        """Get total meditation time in minutes"""
        try:
            conn = sqlite3.connect(self.controller.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT SUM(duration) FROM meditation_sessions')
            total = cursor.fetchone()[0] or 0
            
            conn.close()
            return total
            
        except Exception as e:
            self.logger.error(f"Error getting total meditation time: {e}")
            return 0


class HealthMonitor:
    """Health metrics monitoring and tracking"""
    
    def __init__(self, health_controller):
        self.controller = health_controller
        self.logger = logging.getLogger(self.__class__.__name__)
        
        self.monitoring_active = False
        self.vital_signs = {
            'heart_rate': None,
            'blood_pressure': None,
            'temperature': None,
            'oxygen_saturation': None
        }
        
        self.health_alerts = []
    
    def start_monitoring(self):
        """Start health monitoring"""
        self.monitoring_active = True
        threading.Thread(target=self._monitoring_loop, daemon=True).start()
        self.logger.info("Health monitoring started")
    
    def _monitoring_loop(self):
        """Main health monitoring loop"""
        while self.monitoring_active:
            try:
                # Check for health alerts
                self._check_health_alerts()
                
                # Monitor vital signs (if connected devices available)
                self._update_vital_signs()
                
                time.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                self.logger.error(f"Error in health monitoring loop: {e}")
                time.sleep(60)
    
    def record_metric(self, metric_type: str, value: float, unit: str, notes: str = "") -> bool:
        """Record a health metric"""
        try:
            conn = sqlite3.connect(self.controller.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO health_metrics (metric_type, value, unit, notes, recorded_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (metric_type, value, unit, notes, datetime.now().isoformat()))
            
            conn.commit()
            conn.close()
            
            self.logger.info(f"Recorded {metric_type}: {value} {unit}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error recording health metric: {e}")
            return False
    
    def _check_health_alerts(self):
        """Check for health-related alerts"""
        try:
            # Check for medication reminders
            # Check for appointment reminders
            # Check for abnormal vital signs
            pass
        except Exception as e:
            self.logger.error(f"Error checking health alerts: {e}")
    
    def _update_vital_signs(self):
        """Update vital signs from connected devices"""
        try:
            # This would integrate with actual health monitoring devices
            # For now, it's a placeholder
            pass
        except Exception as e:
            self.logger.error(f"Error updating vital signs: {e}")


class SleepTracker:
    """Sleep tracking and analysis"""
    
    def __init__(self, health_controller):
        self.controller = health_controller
        self.logger = logging.getLogger(self.__class__.__name__)
        
        self.sleep_session = None
        self.sleep_start_time = None
    
    def start_sleep_tracking(self) -> bool:
        """Start sleep tracking"""
        try:
            if self.sleep_session:
                return False  # Already tracking
            
            self.sleep_session = {
                'start_time': datetime.now(),
                'quality_events': []
            }
            
            self.sleep_start_time = datetime.now()
            self.logger.info("Sleep tracking started")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error starting sleep tracking: {e}")
            return False
    
    def end_sleep_tracking(self) -> bool:
        """End sleep tracking"""
        try:
            if not self.sleep_session:
                return False
            
            end_time = datetime.now()
            duration = (end_time - self.sleep_session['start_time']).total_seconds() / 3600  # hours
            
            # Calculate sleep quality score (simplified)
            quality_score = self._calculate_sleep_quality(duration)
            
            # Save sleep data
            conn = sqlite3.connect(self.controller.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO sleep_data (sleep_start, sleep_end, duration, quality_score, created_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                self.sleep_session['start_time'].isoformat(),
                end_time.isoformat(),
                int(duration * 60),  # Convert to minutes
                quality_score,
                datetime.now().isoformat()
            ))
            
            conn.commit()
            conn.close()
            
            self.logger.info(f"Sleep tracking ended: {duration:.1f} hours")
            self.sleep_session = None
            self.sleep_start_time = None
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error ending sleep tracking: {e}")
            return False
    
    def _calculate_sleep_quality(self, duration: float) -> int:
        """Calculate sleep quality score (1-10)"""
        try:
            # Simplified quality calculation based on duration
            if 7 <= duration <= 9:
                return 9  # Optimal sleep duration
            elif 6 <= duration < 7 or 9 < duration <= 10:
                return 7  # Good sleep duration
            elif 5 <= duration < 6 or 10 < duration <= 11:
                return 5  # Fair sleep duration
            else:
                return 3  # Poor sleep duration
                
        except Exception as e:
            self.logger.error(f"Error calculating sleep quality: {e}")
            return 5
    
    def is_tracking(self) -> bool:
        """Check if sleep tracking is active"""
        return self.sleep_session is not None
    
    def get_last_sleep_stats(self) -> Dict:
        """Get last sleep session statistics"""
        try:
            conn = sqlite3.connect(self.controller.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM sleep_data 
                ORDER BY created_at DESC 
                LIMIT 1
            ''')
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return {
                    'duration_hours': row[3] / 60,  # Convert minutes to hours
                    'quality_score': row[4],
                    'sleep_start': row[1],
                    'sleep_end': row[2]
                }
            
            return {}
            
        except Exception as e:
            self.logger.error(f"Error getting last sleep stats: {e}")
            return {}
    
    def get_last_sleep_duration(self) -> float:
        """Get last sleep duration in hours"""
        stats = self.get_last_sleep_stats()
        return stats.get('duration_hours', 0)
    
    def get_average_sleep_quality(self) -> float:
        """Get average sleep quality over last 7 days"""
        try:
            week_start = (datetime.now() - timedelta(days=7)).isoformat()
            
            conn = sqlite3.connect(self.controller.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT AVG(quality_score) FROM sleep_data 
                WHERE created_at >= ?
            ''', (week_start,))
            
            avg_quality = cursor.fetchone()[0] or 0
            conn.close()
            
            return avg_quality
            
        except Exception as e:
            self.logger.error(f"Error getting average sleep quality: {e}")
            return 0


class PostureMonitor:
    """Posture monitoring using computer vision"""
    
    def __init__(self, health_controller):
        self.controller = health_controller
        self.logger = logging.getLogger(self.__class__.__name__)
        
        self.monitoring_active = False
        self.posture_score = 0
        self.poor_posture_alerts = 0
        self.last_posture_check = None
    
    def start_monitoring(self):
        """Start posture monitoring"""
        if hasattr(self.controller.assistant, 'computer_vision'):
            self.monitoring_active = True
            threading.Thread(target=self._posture_monitoring_loop, daemon=True).start()
            self.logger.info("Posture monitoring started")
    
    def _posture_monitoring_loop(self):
        """Main posture monitoring loop"""
        while self.monitoring_active:
            try:
                # Check posture every 30 seconds
                posture_data = self.check_current_posture()
                
                if not posture_data['good_posture']:
                    self.poor_posture_alerts += 1
                    
                    # Alert after 3 consecutive poor posture detections
                    if self.poor_posture_alerts >= 3:
                        self._send_posture_alert()
                        self.poor_posture_alerts = 0
                else:
                    self.poor_posture_alerts = 0
                
                time.sleep(30)
                
            except Exception as e:
                self.logger.error(f"Error in posture monitoring: {e}")
                time.sleep(30)
    
    def check_current_posture(self) -> Dict:
        """Check current posture using computer vision"""
        try:
            if hasattr(self.controller.assistant, 'computer_vision'):
                cv_controller = self.controller.assistant.computer_vision
                
                # Get current pose data
                pose_data = cv_controller.tracking_data.get('poses', [])
                
                if pose_data:
                    # Analyze posture from pose landmarks
                    posture_analysis = self._analyze_posture(pose_data[0])
                    self.posture_score = posture_analysis['score']
                    self.last_posture_check = datetime.now()
                    
                    return posture_analysis
            
            # Default response if no computer vision available
            return {
                'good_posture': True,
                'score': 8,
                'issues': [],
                'suggestions': []
            }
            
        except Exception as e:
            self.logger.error(f"Error checking posture: {e}")
            return {'good_posture': True, 'score': 5, 'issues': [], 'suggestions': []}
    
    def _analyze_posture(self, pose_data: Dict) -> Dict:
        """Analyze posture from pose landmarks"""
        try:
            landmarks = pose_data.get('landmarks', [])
            
            if not landmarks:
                return {'good_posture': True, 'score': 5, 'issues': [], 'suggestions': []}
            
            issues = []
            suggestions = []
            score = 10
            
            # Get key body points
            left_shoulder = landmarks[11]
            right_shoulder = landmarks[12]
            nose = landmarks[0]
            left_ear = landmarks[7]
            right_ear = landmarks[8]
            
            # Check shoulder alignment
            shoulder_diff = abs(left_shoulder[1] - right_shoulder[1])
            if shoulder_diff > 0.05:  # Threshold for shoulder misalignment
                issues.append("Uneven shoulders")
                suggestions.append("Align your shoulders")
                score -= 2
            
            # Check head position (forward head posture)
            ear_avg_x = (left_ear[0] + right_ear[0]) / 2
            shoulder_avg_x = (left_shoulder[0] + right_shoulder[0]) / 2
            
            if ear_avg_x > shoulder_avg_x + 0.05:  # Head too far forward
                issues.append("Forward head posture")
                suggestions.append("Pull your head back and align with shoulders")
                score -= 3
            
            # Check overall posture score
            good_posture = score >= 7
            
            return {
                'good_posture': good_posture,
                'score': score,
                'issues': issues,
                'suggestions': suggestions
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing posture: {e}")
            return {'good_posture': True, 'score': 5, 'issues': [], 'suggestions': []}
    
    def _send_posture_alert(self):
        """Send posture correction alert"""
        try:
            if hasattr(self.controller.assistant, 'voice_controller'):
                self.controller.assistant.voice_controller.speak(
                    "Posture reminder: Please sit up straight and align your shoulders."
                )
            
            self.controller.assistant.emit_event('posture_alert', {
                'message': 'Poor posture detected',
                'suggestions': ['Sit up straight', 'Align shoulders', 'Adjust monitor height']
            })
            
        except Exception as e:
            self.logger.error(f"Error sending posture alert: {e}")
    
    def is_monitoring(self) -> bool:
        """Check if posture monitoring is active"""
        return self.monitoring_active
    
    def get_current_score(self) -> int:
        """Get current posture score"""
        return self.posture_score


class NutritionTracker:
    """Nutrition tracking and management"""
    
    def __init__(self, health_controller):
        self.controller = health_controller
        self.logger = logging.getLogger(self.__class__.__name__)
        
        self.water_reminders_active = False
        self.daily_water_goal = 8  # glasses
        self.water_intake_today = 0
    
    def log_food(self, food_item: str, meal_type: str = "snack", 
                 calories: int = None, protein: float = None,
                 carbs: float = None, fat: float = None) -> bool:
        """Log a food item"""
        try:
            # Estimate nutrition if not provided
            if calories is None:
                nutrition = self._estimate_nutrition(food_item)
                calories = nutrition.get('calories', 100)
                protein = nutrition.get('protein', 5)
                carbs = nutrition.get('carbs', 15)
                fat = nutrition.get('fat', 3)
            
            conn = sqlite3.connect(self.controller.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO nutrition_entries (meal_type, food_item, calories, protein, carbs, fat, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (meal_type, food_item, calories, protein, carbs, fat, datetime.now().isoformat()))
            
            conn.commit()
            conn.close()
            
            self.logger.info(f"Logged food: {food_item}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error logging food: {e}")
            return False
    
    def _estimate_nutrition(self, food_item: str) -> Dict:
        """Estimate nutrition values for food item"""
        # Simplified nutrition estimation
        # In reality, this would use a nutrition database
        
        nutrition_db = {
            'apple': {'calories': 80, 'protein': 0, 'carbs': 22, 'fat': 0},
            'banana': {'calories': 105, 'protein': 1, 'carbs': 27, 'fat': 0},
            'chicken breast': {'calories': 165, 'protein': 31, 'carbs': 0, 'fat': 4},
            'rice': {'calories': 130, 'protein': 3, 'carbs': 28, 'fat': 0},
            'salad': {'calories': 50, 'protein': 3, 'carbs': 10, 'fat': 0}
        }
        
        food_lower = food_item.lower()
        
        for food, nutrition in nutrition_db.items():
            if food in food_lower:
                return nutrition
        
        # Default values
        return {'calories': 100, 'protein': 5, 'carbs': 15, 'fat': 3}
    
    def set_water_reminder(self, interval_minutes: int = 60):
        """Set water drinking reminders"""
        try:
            self.water_reminders_active = True
            threading.Thread(target=self._water_reminder_loop, args=(interval_minutes,), daemon=True).start()
            self.logger.info(f"Water reminders set for every {interval_minutes} minutes")
            
        except Exception as e:
            self.logger.error(f"Error setting water reminder: {e}")
    
    def _water_reminder_loop(self, interval_minutes: int):
        """Water reminder loop"""
        while self.water_reminders_active:
            try:
                time.sleep(interval_minutes * 60)
                
                if hasattr(self.controller.assistant, 'voice_controller'):
                    self.controller.assistant.voice_controller.speak(
                        "Time to drink some water! Stay hydrated."
                    )
                
            except Exception as e:
                self.logger.error(f"Error in water reminder loop: {e}")
                time.sleep(60)
    
    def log_water_intake(self, glasses: int = 1):
        """Log water intake"""
        self.water_intake_today += glasses
        self.logger.info(f"Logged {glasses} glasses of water")


class MentalHealthAssistant:
    """Mental health and mood tracking assistant"""
    
    def __init__(self, health_controller):
        self.controller = health_controller
        self.logger = logging.getLogger(self.__class__.__name__)
        
        self.current_mood_assessment = None
        self.stress_relief_techniques = [
            "Take 5 deep breaths",
            "Go for a short walk",
            "Listen to calming music",
            "Practice progressive muscle relaxation",
            "Write in a journal",
            "Call a friend or family member",
            "Do some light stretching",
            "Practice mindfulness meditation"
        ]
    
    def start_mood_assessment(self):
        """Start mood assessment process"""
        try:
            self.current_mood_assessment = {
                'start_time': datetime.now(),
                'mood_score': None,
                'stress_level': None,
                'anxiety_level': None,
                'energy_level': None,
                'notes': ''
            }
            
            self.logger.info("Started mood assessment")
            
        except Exception as e:
            self.logger.error(f"Error starting mood assessment: {e}")
    
    def record_mood_entry(self, mood_score: int, stress_level: int = 5,
                         anxiety_level: int = 5, energy_level: int = 5,
                         notes: str = "") -> bool:
        """Record a mental health entry"""
        try:
            conn = sqlite3.connect(self.controller.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO mental_health_entries (mood_score, stress_level, anxiety_level, energy_level, notes, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (mood_score, stress_level, anxiety_level, energy_level, notes, datetime.now().isoformat()))
            
            conn.commit()
            conn.close()
            
            self.logger.info(f"Recorded mood entry: mood={mood_score}, stress={stress_level}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error recording mood entry: {e}")
            return False
    
    def get_stress_relief_suggestions(self) -> List[str]:
        """Get personalized stress relief suggestions"""
        try:
            # Return random selection of stress relief techniques
            import random
            return random.sample(self.stress_relief_techniques, 3)
            
        except Exception as e:
            self.logger.error(f"Error getting stress relief suggestions: {e}")
            return self.stress_relief_techniques[:3]
    
    def get_average_mood(self) -> float:
        """Get average mood over last 7 days"""
        try:
            week_start = (datetime.now() - timedelta(days=7)).isoformat()
            
            conn = sqlite3.connect(self.controller.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT AVG(mood_score) FROM mental_health_entries 
                WHERE created_at >= ?
            ''', (week_start,))
            
            avg_mood = cursor.fetchone()[0] or 5
            conn.close()
            
            return avg_mood
            
        except Exception as e:
            self.logger.error(f"Error getting average mood: {e}")
            return 5.0
    
    def get_current_stress_level(self) -> int:
        """Get most recent stress level"""
        try:
            conn = sqlite3.connect(self.controller.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT stress_level FROM mental_health_entries 
                ORDER BY created_at DESC 
                LIMIT 1
            ''')
            
            result = cursor.fetchone()
            conn.close()
            
            return result[0] if result else 5
            
        except Exception as e:
            self.logger.error(f"Error getting current stress level: {e}")
            return 5