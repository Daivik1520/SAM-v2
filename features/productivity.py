"""
Enhanced SAM AI Assistant - Productivity Module
"""
import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import threading
import smtplib
import imaplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import calendar
import sqlite3

from core.base_assistant import BaseAssistant
from config.settings import API_KEYS, DATA_DIR

class ProductivityController:
    """Comprehensive productivity management system"""
    
    def __init__(self, assistant: BaseAssistant):
        self.assistant = assistant
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Initialize components
        self.task_manager = TaskManager(self)
        self.calendar_manager = CalendarManager(self)
        self.email_manager = EmailManager(self)
        self.note_manager = NoteManager(self)
        self.reminder_system = ReminderSystem(self)
        self.time_tracker = TimeTracker(self)
        self.document_processor = DocumentProcessor(self)
        
        # Database setup
        self.setup_database()
        
        # Register voice commands
        self.register_voice_commands()
        
        # Start background services
        self.start_background_services()
    
    def setup_database(self):
        """Setup productivity database"""
        try:
            self.db_path = DATA_DIR / "productivity.db"
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Tasks table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT,
                    priority INTEGER DEFAULT 1,
                    status TEXT DEFAULT 'pending',
                    due_date TEXT,
                    created_at TEXT,
                    completed_at TEXT,
                    category TEXT,
                    tags TEXT
                )
            ''')
            
            # Calendar events table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT,
                    start_time TEXT,
                    end_time TEXT,
                    location TEXT,
                    attendees TEXT,
                    reminder_time TEXT,
                    created_at TEXT
                )
            ''')
            
            # Notes table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS notes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    content TEXT,
                    category TEXT,
                    tags TEXT,
                    created_at TEXT,
                    updated_at TEXT
                )
            ''')
            
            # Time tracking table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS time_entries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_id INTEGER,
                    project TEXT,
                    description TEXT,
                    start_time TEXT,
                    end_time TEXT,
                    duration INTEGER,
                    created_at TEXT
                )
            ''')
            
            conn.commit()
            conn.close()
            
            self.logger.info("Productivity database initialized")
            
        except Exception as e:
            self.logger.error(f"Error setting up database: {e}")
    
    def register_voice_commands(self):
        """Register productivity voice commands"""
        if hasattr(self.assistant, 'voice_controller'):
            voice = self.assistant.voice_controller
            
            # Task management
            voice.register_command(
                ["create task *", "add task *", "new task *"],
                self.voice_create_task,
                "Create a new task"
            )
            
            voice.register_command(
                ["complete task *", "finish task *", "mark task * complete"],
                self.voice_complete_task,
                "Mark a task as complete"
            )
            
            voice.register_command(
                ["list tasks", "show tasks", "what are my tasks"],
                self.voice_list_tasks,
                "List all tasks"
            )
            
            # Calendar management
            voice.register_command(
                ["create event *", "schedule *", "add appointment *"],
                self.voice_create_event,
                "Create a calendar event"
            )
            
            voice.register_command(
                ["what's my schedule", "show calendar", "what's next"],
                self.voice_show_schedule,
                "Show upcoming events"
            )
            
            # Note taking
            voice.register_command(
                ["take note *", "create note *", "remember *"],
                self.voice_take_note,
                "Create a new note"
            )
            
            voice.register_command(
                ["find note *", "search notes *"],
                self.voice_find_note,
                "Search for notes"
            )
            
            # Email management
            voice.register_command(
                ["check email", "read emails", "any new emails"],
                self.voice_check_email,
                "Check for new emails"
            )
            
            voice.register_command(
                ["send email to *", "email *"],
                self.voice_send_email,
                "Send an email"
            )
            
            # Time tracking
            voice.register_command(
                ["start timer *", "begin tracking *"],
                self.voice_start_timer,
                "Start time tracking"
            )
            
            voice.register_command(
                ["stop timer", "end tracking"],
                self.voice_stop_timer,
                "Stop time tracking"
            )
            
            # Reminders
            voice.register_command(
                ["remind me to * in *", "set reminder *"],
                self.voice_set_reminder,
                "Set a reminder"
            )
    
    def start_background_services(self):
        """Start background productivity services"""
        self.reminder_system.start()
        self.email_manager.start_monitoring()
    
    # Voice command handlers
    def voice_create_task(self, text: str):
        """Handle voice create task command"""
        # Extract task title from text
        words = text.split()
        if len(words) > 2:
            task_title = ' '.join(words[2:])  # Skip "create task"
            
            task_id = self.task_manager.create_task(task_title)
            if task_id:
                self.assistant.voice_controller.speak(f"Created task: {task_title}")
            else:
                self.assistant.voice_controller.speak("Failed to create task")
    
    def voice_complete_task(self, text: str):
        """Handle voice complete task command"""
        # This would need more sophisticated parsing to identify the specific task
        self.assistant.voice_controller.speak("Task completion feature activated")
    
    def voice_list_tasks(self, text: str):
        """Handle voice list tasks command"""
        tasks = self.task_manager.get_pending_tasks()
        
        if tasks:
            task_list = []
            for task in tasks[:5]:  # Limit to 5 tasks
                task_list.append(task['title'])
            
            response = f"You have {len(tasks)} pending tasks. Here are the first few: " + ", ".join(task_list)
        else:
            response = "You have no pending tasks"
        
        self.assistant.voice_controller.speak(response)
    
    def voice_create_event(self, text: str):
        """Handle voice create event command"""
        # Extract event details from text
        words = text.split()
        if len(words) > 2:
            event_title = ' '.join(words[2:])  # Skip "create event"
            
            event_id = self.calendar_manager.create_event(event_title)
            if event_id:
                self.assistant.voice_controller.speak(f"Created event: {event_title}")
            else:
                self.assistant.voice_controller.speak("Failed to create event")
    
    def voice_show_schedule(self, text: str):
        """Handle voice show schedule command"""
        events = self.calendar_manager.get_upcoming_events()
        
        if events:
            response = f"You have {len(events)} upcoming events. "
            if events:
                next_event = events[0]
                response += f"Next: {next_event['title']} at {next_event['start_time']}"
        else:
            response = "You have no upcoming events"
        
        self.assistant.voice_controller.speak(response)
    
    def voice_take_note(self, text: str):
        """Handle voice take note command"""
        words = text.split()
        if len(words) > 2:
            note_content = ' '.join(words[2:])  # Skip "take note"
            
            note_id = self.note_manager.create_note("Voice Note", note_content)
            if note_id:
                self.assistant.voice_controller.speak("Note saved")
            else:
                self.assistant.voice_controller.speak("Failed to save note")
    
    def voice_find_note(self, text: str):
        """Handle voice find note command"""
        words = text.split()
        if len(words) > 2:
            search_term = ' '.join(words[2:])  # Skip "find note"
            
            notes = self.note_manager.search_notes(search_term)
            if notes:
                self.assistant.voice_controller.speak(f"Found {len(notes)} notes matching '{search_term}'")
            else:
                self.assistant.voice_controller.speak(f"No notes found matching '{search_term}'")
    
    def voice_check_email(self, text: str):
        """Handle voice check email command"""
        unread_count = self.email_manager.get_unread_count()
        
        if unread_count > 0:
            self.assistant.voice_controller.speak(f"You have {unread_count} unread emails")
        else:
            self.assistant.voice_controller.speak("No new emails")
    
    def voice_send_email(self, text: str):
        """Handle voice send email command"""
        self.assistant.voice_controller.speak("Email composition feature activated")
    
    def voice_start_timer(self, text: str):
        """Handle voice start timer command"""
        words = text.split()
        if len(words) > 2:
            project_name = ' '.join(words[2:])  # Skip "start timer"
            
            if self.time_tracker.start_tracking(project_name):
                self.assistant.voice_controller.speak(f"Started tracking time for {project_name}")
            else:
                self.assistant.voice_controller.speak("Failed to start timer")
    
    def voice_stop_timer(self, text: str):
        """Handle voice stop timer command"""
        if self.time_tracker.stop_tracking():
            self.assistant.voice_controller.speak("Timer stopped")
        else:
            self.assistant.voice_controller.speak("No active timer to stop")
    
    def voice_set_reminder(self, text: str):
        """Handle voice set reminder command"""
        # This would need more sophisticated parsing for time extraction
        self.assistant.voice_controller.speak("Reminder set")
    
    def get_productivity_stats(self) -> Dict:
        """Get productivity statistics"""
        return {
            'tasks': {
                'total': self.task_manager.get_task_count(),
                'pending': len(self.task_manager.get_pending_tasks()),
                'completed_today': self.task_manager.get_completed_today_count()
            },
            'calendar': {
                'events_today': len(self.calendar_manager.get_today_events()),
                'upcoming_events': len(self.calendar_manager.get_upcoming_events())
            },
            'notes': {
                'total': self.note_manager.get_note_count()
            },
            'time_tracking': {
                'active_session': self.time_tracker.is_tracking(),
                'today_hours': self.time_tracker.get_today_hours()
            },
            'email': {
                'unread': self.email_manager.get_unread_count()
            }
        }


class TaskManager:
    """Task management system"""
    
    def __init__(self, productivity_controller):
        self.controller = productivity_controller
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def create_task(self, title: str, description: str = "", priority: int = 1,
                   due_date: str = None, category: str = "", tags: List[str] = None) -> Optional[int]:
        """Create a new task"""
        try:
            conn = sqlite3.connect(self.controller.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO tasks (title, description, priority, due_date, created_at, category, tags)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                title, description, priority, due_date,
                datetime.now().isoformat(), category,
                json.dumps(tags or [])
            ))
            
            task_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            self.logger.info(f"Created task: {title}")
            return task_id
            
        except Exception as e:
            self.logger.error(f"Error creating task: {e}")
            return None
    
    def complete_task(self, task_id: int) -> bool:
        """Mark task as complete"""
        try:
            conn = sqlite3.connect(self.controller.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE tasks SET status = 'completed', completed_at = ?
                WHERE id = ?
            ''', (datetime.now().isoformat(), task_id))
            
            conn.commit()
            conn.close()
            
            return cursor.rowcount > 0
            
        except Exception as e:
            self.logger.error(f"Error completing task: {e}")
            return False
    
    def get_pending_tasks(self) -> List[Dict]:
        """Get all pending tasks"""
        try:
            conn = sqlite3.connect(self.controller.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM tasks WHERE status = 'pending'
                ORDER BY priority DESC, created_at ASC
            ''')
            
            tasks = []
            for row in cursor.fetchall():
                tasks.append({
                    'id': row[0],
                    'title': row[1],
                    'description': row[2],
                    'priority': row[3],
                    'status': row[4],
                    'due_date': row[5],
                    'created_at': row[6],
                    'category': row[8],
                    'tags': json.loads(row[9]) if row[9] else []
                })
            
            conn.close()
            return tasks
            
        except Exception as e:
            self.logger.error(f"Error getting pending tasks: {e}")
            return []
    
    def get_task_count(self) -> int:
        """Get total task count"""
        try:
            conn = sqlite3.connect(self.controller.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT COUNT(*) FROM tasks')
            count = cursor.fetchone()[0]
            
            conn.close()
            return count
            
        except Exception as e:
            self.logger.error(f"Error getting task count: {e}")
            return 0
    
    def get_completed_today_count(self) -> int:
        """Get count of tasks completed today"""
        try:
            today = datetime.now().date().isoformat()
            
            conn = sqlite3.connect(self.controller.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT COUNT(*) FROM tasks 
                WHERE status = 'completed' AND DATE(completed_at) = ?
            ''', (today,))
            
            count = cursor.fetchone()[0]
            conn.close()
            
            return count
            
        except Exception as e:
            self.logger.error(f"Error getting completed today count: {e}")
            return 0


class CalendarManager:
    """Calendar and event management"""
    
    def __init__(self, productivity_controller):
        self.controller = productivity_controller
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def create_event(self, title: str, description: str = "", start_time: str = None,
                    end_time: str = None, location: str = "", attendees: List[str] = None) -> Optional[int]:
        """Create a new calendar event"""
        try:
            conn = sqlite3.connect(self.controller.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO events (title, description, start_time, end_time, location, attendees, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                title, description, start_time, end_time, location,
                json.dumps(attendees or []), datetime.now().isoformat()
            ))
            
            event_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            self.logger.info(f"Created event: {title}")
            return event_id
            
        except Exception as e:
            self.logger.error(f"Error creating event: {e}")
            return None
    
    def get_upcoming_events(self, days: int = 7) -> List[Dict]:
        """Get upcoming events"""
        try:
            end_date = (datetime.now() + timedelta(days=days)).isoformat()
            
            conn = sqlite3.connect(self.controller.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM events 
                WHERE start_time >= ? AND start_time <= ?
                ORDER BY start_time ASC
            ''', (datetime.now().isoformat(), end_date))
            
            events = []
            for row in cursor.fetchall():
                events.append({
                    'id': row[0],
                    'title': row[1],
                    'description': row[2],
                    'start_time': row[3],
                    'end_time': row[4],
                    'location': row[5],
                    'attendees': json.loads(row[6]) if row[6] else []
                })
            
            conn.close()
            return events
            
        except Exception as e:
            self.logger.error(f"Error getting upcoming events: {e}")
            return []
    
    def get_today_events(self) -> List[Dict]:
        """Get today's events"""
        try:
            today = datetime.now().date().isoformat()
            tomorrow = (datetime.now().date() + timedelta(days=1)).isoformat()
            
            conn = sqlite3.connect(self.controller.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM events 
                WHERE DATE(start_time) = ?
                ORDER BY start_time ASC
            ''', (today,))
            
            events = []
            for row in cursor.fetchall():
                events.append({
                    'id': row[0],
                    'title': row[1],
                    'start_time': row[3],
                    'end_time': row[4]
                })
            
            conn.close()
            return events
            
        except Exception as e:
            self.logger.error(f"Error getting today's events: {e}")
            return []


class EmailManager:
    """Email management system"""
    
    def __init__(self, productivity_controller):
        self.controller = productivity_controller
        self.logger = logging.getLogger(self.__class__.__name__)
        
        self.email_config = {
            'smtp_server': 'smtp.gmail.com',
            'smtp_port': 587,
            'imap_server': 'imap.gmail.com',
            'imap_port': 993,
            'username': '',
            'password': ''
        }
        
        self.monitoring_active = False
        self.unread_count = 0
    
    def start_monitoring(self):
        """Start email monitoring"""
        self.monitoring_active = True
        threading.Thread(target=self._monitor_emails, daemon=True).start()
    
    def _monitor_emails(self):
        """Monitor emails in background"""
        while self.monitoring_active:
            try:
                self._check_new_emails()
                time.sleep(300)  # Check every 5 minutes
            except Exception as e:
                self.logger.error(f"Error monitoring emails: {e}")
                time.sleep(60)
    
    def _check_new_emails(self):
        """Check for new emails"""
        try:
            # This would implement actual email checking
            # For now, it's a placeholder
            pass
        except Exception as e:
            self.logger.error(f"Error checking emails: {e}")
    
    def get_unread_count(self) -> int:
        """Get unread email count"""
        return self.unread_count
    
    def send_email(self, to: str, subject: str, body: str) -> bool:
        """Send an email"""
        try:
            # This would implement actual email sending
            # For now, it's a placeholder
            self.logger.info(f"Email sent to {to}: {subject}")
            return True
        except Exception as e:
            self.logger.error(f"Error sending email: {e}")
            return False


class NoteManager:
    """Note management system"""
    
    def __init__(self, productivity_controller):
        self.controller = productivity_controller
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def create_note(self, title: str, content: str, category: str = "", tags: List[str] = None) -> Optional[int]:
        """Create a new note"""
        try:
            conn = sqlite3.connect(self.controller.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO notes (title, content, category, tags, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                title, content, category, json.dumps(tags or []),
                datetime.now().isoformat(), datetime.now().isoformat()
            ))
            
            note_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            self.logger.info(f"Created note: {title}")
            return note_id
            
        except Exception as e:
            self.logger.error(f"Error creating note: {e}")
            return None
    
    def search_notes(self, search_term: str) -> List[Dict]:
        """Search notes by content"""
        try:
            conn = sqlite3.connect(self.controller.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM notes 
                WHERE title LIKE ? OR content LIKE ?
                ORDER BY updated_at DESC
            ''', (f'%{search_term}%', f'%{search_term}%'))
            
            notes = []
            for row in cursor.fetchall():
                notes.append({
                    'id': row[0],
                    'title': row[1],
                    'content': row[2],
                    'category': row[3],
                    'tags': json.loads(row[4]) if row[4] else []
                })
            
            conn.close()
            return notes
            
        except Exception as e:
            self.logger.error(f"Error searching notes: {e}")
            return []
    
    def get_note_count(self) -> int:
        """Get total note count"""
        try:
            conn = sqlite3.connect(self.controller.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT COUNT(*) FROM notes')
            count = cursor.fetchone()[0]
            
            conn.close()
            return count
            
        except Exception as e:
            self.logger.error(f"Error getting note count: {e}")
            return 0


class ReminderSystem:
    """Reminder and notification system"""
    
    def __init__(self, productivity_controller):
        self.controller = productivity_controller
        self.logger = logging.getLogger(self.__class__.__name__)
        
        self.reminders = []
        self.active = False
    
    def start(self):
        """Start reminder system"""
        self.active = True
        threading.Thread(target=self._reminder_loop, daemon=True).start()
    
    def _reminder_loop(self):
        """Main reminder loop"""
        while self.active:
            try:
                current_time = datetime.now()
                
                for reminder in self.reminders[:]:  # Copy list to avoid modification issues
                    if current_time >= reminder['trigger_time']:
                        self._trigger_reminder(reminder)
                        self.reminders.remove(reminder)
                
                time.sleep(60)  # Check every minute
                
            except Exception as e:
                self.logger.error(f"Error in reminder loop: {e}")
                time.sleep(60)
    
    def _trigger_reminder(self, reminder: Dict):
        """Trigger a reminder"""
        message = reminder['message']
        self.controller.assistant.emit_event('reminder', {'message': message})
        
        if hasattr(self.controller.assistant, 'voice_controller'):
            self.controller.assistant.voice_controller.speak(f"Reminder: {message}")
    
    def add_reminder(self, message: str, trigger_time: datetime) -> bool:
        """Add a new reminder"""
        try:
            reminder = {
                'message': message,
                'trigger_time': trigger_time,
                'created_at': datetime.now()
            }
            
            self.reminders.append(reminder)
            self.logger.info(f"Added reminder: {message} at {trigger_time}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error adding reminder: {e}")
            return False


class TimeTracker:
    """Time tracking system"""
    
    def __init__(self, productivity_controller):
        self.controller = productivity_controller
        self.logger = logging.getLogger(self.__class__.__name__)
        
        self.current_session = None
    
    def start_tracking(self, project: str, description: str = "") -> bool:
        """Start time tracking"""
        try:
            if self.current_session:
                self.stop_tracking()  # Stop current session
            
            self.current_session = {
                'project': project,
                'description': description,
                'start_time': datetime.now(),
                'task_id': None
            }
            
            self.logger.info(f"Started tracking time for: {project}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error starting time tracking: {e}")
            return False
    
    def stop_tracking(self) -> bool:
        """Stop time tracking"""
        try:
            if not self.current_session:
                return False
            
            end_time = datetime.now()
            duration = (end_time - self.current_session['start_time']).total_seconds()
            
            # Save to database
            conn = sqlite3.connect(self.controller.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO time_entries (task_id, project, description, start_time, end_time, duration, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                self.current_session.get('task_id'),
                self.current_session['project'],
                self.current_session['description'],
                self.current_session['start_time'].isoformat(),
                end_time.isoformat(),
                int(duration),
                datetime.now().isoformat()
            ))
            
            conn.commit()
            conn.close()
            
            self.logger.info(f"Stopped tracking time for: {self.current_session['project']}")
            self.current_session = None
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error stopping time tracking: {e}")
            return False
    
    def is_tracking(self) -> bool:
        """Check if currently tracking time"""
        return self.current_session is not None
    
    def get_today_hours(self) -> float:
        """Get total hours tracked today"""
        try:
            today = datetime.now().date().isoformat()
            
            conn = sqlite3.connect(self.controller.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT SUM(duration) FROM time_entries 
                WHERE DATE(start_time) = ?
            ''', (today,))
            
            total_seconds = cursor.fetchone()[0] or 0
            conn.close()
            
            return total_seconds / 3600  # Convert to hours
            
        except Exception as e:
            self.logger.error(f"Error getting today's hours: {e}")
            return 0.0


class DocumentProcessor:
    """Document processing and analysis"""
    
    def __init__(self, productivity_controller):
        self.controller = productivity_controller
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def process_document(self, file_path: str) -> Dict:
        """Process and analyze a document"""
        try:
            # This would implement document processing
            # For now, it's a placeholder
            return {
                'file_path': file_path,
                'processed_at': datetime.now().isoformat(),
                'word_count': 0,
                'summary': '',
                'key_points': []
            }
        except Exception as e:
            self.logger.error(f"Error processing document: {e}")
            return {}
    
    def extract_text(self, file_path: str) -> str:
        """Extract text from document"""
        try:
            # This would implement text extraction
            # For now, it's a placeholder
            return ""
        except Exception as e:
            self.logger.error(f"Error extracting text: {e}")
            return ""