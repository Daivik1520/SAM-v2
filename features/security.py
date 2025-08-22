"""
Enhanced SAM AI Assistant - Security Module
"""
import asyncio
import hashlib
import json
import logging
import os
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import threading
import sqlite3
from cryptography.fernet import Fernet
import cv2
import numpy as np

from core.base_assistant import BaseAssistant
from config.settings import DATA_DIR, SECURITY_CONFIG

class SecurityController:
    """Comprehensive security and privacy management system"""
    
    def __init__(self, assistant: BaseAssistant):
        self.assistant = assistant
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Initialize components
        self.authentication_manager = AuthenticationManager(self)
        self.encryption_manager = EncryptionManager(self)
        self.privacy_manager = PrivacyManager(self)
        self.access_control = AccessControl(self)
        self.security_monitor = SecurityMonitor(self)
        self.biometric_auth = BiometricAuthentication(self)
        self.session_manager = SessionManager(self)
        
        # Security state
        self.security_level = "normal"  # normal, high, maximum
        self.privacy_mode = SECURITY_CONFIG["privacy_mode"]
        self.authenticated_user = None
        self.failed_attempts = 0
        self.lockout_until = None
        
        # Database setup
        self.setup_database()
        
        # Register voice commands
        self.register_voice_commands()
        
        # Start security monitoring
        self.start_security_monitoring()
    
    def setup_database(self):
        """Setup security database"""
        try:
            self.db_path = DATA_DIR / "security.db"
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    salt TEXT NOT NULL,
                    email TEXT,
                    role TEXT DEFAULT 'user',
                    created_at TEXT,
                    last_login TEXT,
                    failed_attempts INTEGER DEFAULT 0,
                    locked_until TEXT
                )
            ''')
            
            # Security events table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS security_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_type TEXT NOT NULL,
                    user_id INTEGER,
                    description TEXT,
                    ip_address TEXT,
                    user_agent TEXT,
                    severity TEXT,
                    created_at TEXT
                )
            ''')
            
            # Sessions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT UNIQUE NOT NULL,
                    user_id INTEGER,
                    created_at TEXT,
                    expires_at TEXT,
                    last_activity TEXT,
                    ip_address TEXT,
                    is_active INTEGER DEFAULT 1
                )
            ''')
            
            # Biometric data table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS biometric_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    biometric_type TEXT,
                    data_hash TEXT,
                    created_at TEXT,
                    last_used TEXT
                )
            ''')
            
            # Access logs table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS access_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    resource TEXT,
                    action TEXT,
                    result TEXT,
                    ip_address TEXT,
                    created_at TEXT
                )
            ''')
            
            conn.commit()
            conn.close()
            
            self.logger.info("Security database initialized")
            
        except Exception as e:
            self.logger.error(f"Error setting up security database: {e}")
    
    def register_voice_commands(self):
        """Register security voice commands"""
        if hasattr(self.assistant, 'voice_controller'):
            voice = self.assistant.voice_controller
            
            # Authentication commands
            voice.register_command(
                ["authenticate", "login", "sign in"],
                self.voice_authenticate,
                "Authenticate user"
            )
            
            voice.register_command(
                ["logout", "sign out", "end session"],
                self.voice_logout,
                "End current session"
            )
            
            # Privacy commands
            voice.register_command(
                ["enable privacy mode", "privacy on"],
                self.voice_enable_privacy_mode,
                "Enable privacy mode"
            )
            
            voice.register_command(
                ["disable privacy mode", "privacy off"],
                self.voice_disable_privacy_mode,
                "Disable privacy mode"
            )
            
            # Security level commands
            voice.register_command(
                ["increase security", "high security", "maximum security"],
                self.voice_increase_security,
                "Increase security level"
            )
            
            voice.register_command(
                ["normal security", "standard security"],
                self.voice_normal_security,
                "Set normal security level"
            )
            
            # Biometric commands
            voice.register_command(
                ["setup face recognition", "register face"],
                self.voice_setup_face_recognition,
                "Setup face recognition"
            )
            
            voice.register_command(
                ["security status", "check security"],
                self.voice_security_status,
                "Check security status"
            )
    
    def start_security_monitoring(self):
        """Start security monitoring services"""
        self.security_monitor.start_monitoring()
        self.session_manager.start_session_cleanup()
    
    # Voice command handlers
    def voice_authenticate(self, text: str):
        """Handle voice authentication command"""
        if self.authenticated_user:
            self.assistant.voice_controller.speak("You are already authenticated")
            return
        
        # Start authentication process
        if SECURITY_CONFIG["biometric_auth"] and self.biometric_auth.is_available():
            self.assistant.voice_controller.speak("Please look at the camera for face recognition")
            if self.biometric_auth.authenticate_face():
                self.assistant.voice_controller.speak("Authentication successful")
            else:
                self.assistant.voice_controller.speak("Face recognition failed. Please try again")
        else:
            self.assistant.voice_controller.speak("Please provide your username and password")
    
    def voice_logout(self, text: str):
        """Handle voice logout command"""
        if self.logout():
            self.assistant.voice_controller.speak("You have been logged out")
        else:
            self.assistant.voice_controller.speak("No active session to logout")
    
    def voice_enable_privacy_mode(self, text: str):
        """Handle voice enable privacy mode command"""
        if self.enable_privacy_mode():
            self.assistant.voice_controller.speak("Privacy mode enabled")
        else:
            self.assistant.voice_controller.speak("Failed to enable privacy mode")
    
    def voice_disable_privacy_mode(self, text: str):
        """Handle voice disable privacy mode command"""
        if self.disable_privacy_mode():
            self.assistant.voice_controller.speak("Privacy mode disabled")
        else:
            self.assistant.voice_controller.speak("Failed to disable privacy mode")
    
    def voice_increase_security(self, text: str):
        """Handle voice increase security command"""
        if "maximum" in text.lower():
            self.set_security_level("maximum")
            self.assistant.voice_controller.speak("Security level set to maximum")
        else:
            self.set_security_level("high")
            self.assistant.voice_controller.speak("Security level set to high")
    
    def voice_normal_security(self, text: str):
        """Handle voice normal security command"""
        self.set_security_level("normal")
        self.assistant.voice_controller.speak("Security level set to normal")
    
    def voice_setup_face_recognition(self, text: str):
        """Handle voice setup face recognition command"""
        if self.biometric_auth.setup_face_recognition():
            self.assistant.voice_controller.speak("Face recognition setup complete")
        else:
            self.assistant.voice_controller.speak("Face recognition setup failed")
    
    def voice_security_status(self, text: str):
        """Handle voice security status command"""
        status = self.get_security_status()
        
        auth_status = "authenticated" if status['authenticated'] else "not authenticated"
        privacy_status = "enabled" if status['privacy_mode'] else "disabled"
        
        response = f"Security status: {auth_status}, privacy mode {privacy_status}, security level {status['security_level']}"
        self.assistant.voice_controller.speak(response)
    
    def authenticate_user(self, username: str, password: str) -> bool:
        """Authenticate user with username and password"""
        try:
            if self.is_locked_out():
                self.logger.warning(f"Authentication attempt during lockout: {username}")
                return False
            
            user = self.authentication_manager.verify_credentials(username, password)
            
            if user:
                self.authenticated_user = user
                self.failed_attempts = 0
                self.lockout_until = None
                
                # Create session
                session_id = self.session_manager.create_session(user['id'])
                
                # Log successful authentication
                self.log_security_event("authentication_success", user['id'], f"User {username} authenticated")
                
                self.logger.info(f"User authenticated: {username}")
                return True
            else:
                self.failed_attempts += 1
                
                # Check for lockout
                if self.failed_attempts >= 3:
                    self.lockout_until = datetime.now() + timedelta(minutes=15)
                    self.log_security_event("account_lockout", None, f"Account locked due to failed attempts: {username}")
                
                self.log_security_event("authentication_failure", None, f"Failed authentication attempt: {username}")
                
                self.logger.warning(f"Authentication failed: {username}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error during authentication: {e}")
            return False
    
    def logout(self) -> bool:
        """Logout current user"""
        try:
            if not self.authenticated_user:
                return False
            
            # End session
            self.session_manager.end_current_session()
            
            # Log logout
            self.log_security_event("logout", self.authenticated_user['id'], "User logged out")
            
            self.logger.info(f"User logged out: {self.authenticated_user['username']}")
            self.authenticated_user = None
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error during logout: {e}")
            return False
    
    def enable_privacy_mode(self) -> bool:
        """Enable privacy mode"""
        try:
            self.privacy_mode = True
            SECURITY_CONFIG["privacy_mode"] = True
            
            # Disable certain features in privacy mode
            self.privacy_manager.apply_privacy_settings()
            
            self.log_security_event("privacy_mode_enabled", 
                                   self.authenticated_user['id'] if self.authenticated_user else None,
                                   "Privacy mode enabled")
            
            self.logger.info("Privacy mode enabled")
            return True
            
        except Exception as e:
            self.logger.error(f"Error enabling privacy mode: {e}")
            return False
    
    def disable_privacy_mode(self) -> bool:
        """Disable privacy mode"""
        try:
            self.privacy_mode = False
            SECURITY_CONFIG["privacy_mode"] = False
            
            # Restore normal settings
            self.privacy_manager.restore_normal_settings()
            
            self.log_security_event("privacy_mode_disabled",
                                   self.authenticated_user['id'] if self.authenticated_user else None,
                                   "Privacy mode disabled")
            
            self.logger.info("Privacy mode disabled")
            return True
            
        except Exception as e:
            self.logger.error(f"Error disabling privacy mode: {e}")
            return False
    
    def set_security_level(self, level: str):
        """Set security level"""
        try:
            if level not in ["normal", "high", "maximum"]:
                level = "normal"
            
            self.security_level = level
            
            # Apply security level settings
            if level == "maximum":
                self.enable_privacy_mode()
                # Enable additional security measures
            elif level == "high":
                # Enable enhanced security measures
                pass
            else:
                # Normal security settings
                pass
            
            self.log_security_event("security_level_changed",
                                   self.authenticated_user['id'] if self.authenticated_user else None,
                                   f"Security level changed to {level}")
            
            self.logger.info(f"Security level set to: {level}")
            
        except Exception as e:
            self.logger.error(f"Error setting security level: {e}")
    
    def is_locked_out(self) -> bool:
        """Check if account is locked out"""
        if self.lockout_until and datetime.now() < self.lockout_until:
            return True
        
        if self.lockout_until and datetime.now() >= self.lockout_until:
            # Reset lockout
            self.lockout_until = None
            self.failed_attempts = 0
        
        return False
    
    def log_security_event(self, event_type: str, user_id: Optional[int], 
                          description: str, severity: str = "info"):
        """Log security event"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO security_events (event_type, user_id, description, severity, created_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (event_type, user_id, description, severity, datetime.now().isoformat()))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error logging security event: {e}")
    
    def get_security_status(self) -> Dict:
        """Get current security status"""
        return {
            'authenticated': self.authenticated_user is not None,
            'username': self.authenticated_user['username'] if self.authenticated_user else None,
            'privacy_mode': self.privacy_mode,
            'security_level': self.security_level,
            'locked_out': self.is_locked_out(),
            'failed_attempts': self.failed_attempts,
            'biometric_available': self.biometric_auth.is_available(),
            'session_active': self.session_manager.has_active_session()
        }


class AuthenticationManager:
    """User authentication management"""
    
    def __init__(self, security_controller):
        self.controller = security_controller
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def create_user(self, username: str, password: str, email: str = "", role: str = "user") -> bool:
        """Create a new user"""
        try:
            # Generate salt and hash password
            salt = os.urandom(32)
            password_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
            
            conn = sqlite3.connect(self.controller.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO users (username, password_hash, salt, email, role, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (username, password_hash.hex(), salt.hex(), email, role, datetime.now().isoformat()))
            
            conn.commit()
            conn.close()
            
            self.logger.info(f"User created: {username}")
            return True
            
        except sqlite3.IntegrityError:
            self.logger.error(f"User already exists: {username}")
            return False
        except Exception as e:
            self.logger.error(f"Error creating user: {e}")
            return False
    
    def verify_credentials(self, username: str, password: str) -> Optional[Dict]:
        """Verify user credentials"""
        try:
            conn = sqlite3.connect(self.controller.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, username, password_hash, salt, email, role, failed_attempts, locked_until
                FROM users WHERE username = ?
            ''', (username,))
            
            user_data = cursor.fetchone()
            
            if not user_data:
                conn.close()
                return None
            
            # Check if account is locked
            if user_data[7]:  # locked_until
                locked_until = datetime.fromisoformat(user_data[7])
                if datetime.now() < locked_until:
                    conn.close()
                    return None
            
            # Verify password
            stored_hash = bytes.fromhex(user_data[2])
            salt = bytes.fromhex(user_data[3])
            password_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
            
            if password_hash == stored_hash:
                # Update last login
                cursor.execute('''
                    UPDATE users SET last_login = ?, failed_attempts = 0, locked_until = NULL
                    WHERE id = ?
                ''', (datetime.now().isoformat(), user_data[0]))
                
                conn.commit()
                conn.close()
                
                return {
                    'id': user_data[0],
                    'username': user_data[1],
                    'email': user_data[4],
                    'role': user_data[5]
                }
            else:
                # Increment failed attempts
                failed_attempts = user_data[6] + 1
                locked_until = None
                
                if failed_attempts >= 3:
                    locked_until = (datetime.now() + timedelta(minutes=15)).isoformat()
                
                cursor.execute('''
                    UPDATE users SET failed_attempts = ?, locked_until = ?
                    WHERE id = ?
                ''', (failed_attempts, locked_until, user_data[0]))
                
                conn.commit()
                conn.close()
                
                return None
                
        except Exception as e:
            self.logger.error(f"Error verifying credentials: {e}")
            return None


class EncryptionManager:
    """Data encryption and decryption management"""
    
    def __init__(self, security_controller):
        self.controller = security_controller
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Initialize encryption key
        self.encryption_key = self._get_or_create_key()
        self.cipher_suite = Fernet(self.encryption_key)
    
    def _get_or_create_key(self) -> bytes:
        """Get existing encryption key or create new one"""
        try:
            key_file = DATA_DIR / "encryption.key"
            
            if key_file.exists():
                with open(key_file, 'rb') as f:
                    return f.read()
            else:
                # Generate new key
                key = Fernet.generate_key()
                
                with open(key_file, 'wb') as f:
                    f.write(key)
                
                # Set restrictive permissions
                os.chmod(key_file, 0o600)
                
                self.logger.info("New encryption key generated")
                return key
                
        except Exception as e:
            self.logger.error(f"Error handling encryption key: {e}")
            return Fernet.generate_key()
    
    def encrypt_data(self, data: str) -> str:
        """Encrypt string data"""
        try:
            encrypted_data = self.cipher_suite.encrypt(data.encode())
            return encrypted_data.decode()
        except Exception as e:
            self.logger.error(f"Error encrypting data: {e}")
            return data
    
    def decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt string data"""
        try:
            decrypted_data = self.cipher_suite.decrypt(encrypted_data.encode())
            return decrypted_data.decode()
        except Exception as e:
            self.logger.error(f"Error decrypting data: {e}")
            return encrypted_data
    
    def encrypt_file(self, file_path: str) -> bool:
        """Encrypt a file"""
        try:
            with open(file_path, 'rb') as f:
                file_data = f.read()
            
            encrypted_data = self.cipher_suite.encrypt(file_data)
            
            with open(file_path + '.encrypted', 'wb') as f:
                f.write(encrypted_data)
            
            # Remove original file
            os.remove(file_path)
            
            self.logger.info(f"File encrypted: {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error encrypting file: {e}")
            return False
    
    def decrypt_file(self, encrypted_file_path: str) -> bool:
        """Decrypt a file"""
        try:
            with open(encrypted_file_path, 'rb') as f:
                encrypted_data = f.read()
            
            decrypted_data = self.cipher_suite.decrypt(encrypted_data)
            
            original_path = encrypted_file_path.replace('.encrypted', '')
            
            with open(original_path, 'wb') as f:
                f.write(decrypted_data)
            
            # Remove encrypted file
            os.remove(encrypted_file_path)
            
            self.logger.info(f"File decrypted: {original_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error decrypting file: {e}")
            return False


class PrivacyManager:
    """Privacy settings and data protection management"""
    
    def __init__(self, security_controller):
        self.controller = security_controller
        self.logger = logging.getLogger(self.__class__.__name__)
        
        self.privacy_settings = {
            'disable_camera': False,
            'disable_microphone': False,
            'disable_location': False,
            'disable_logging': False,
            'anonymize_data': False,
            'auto_delete_logs': False
        }
    
    def apply_privacy_settings(self):
        """Apply privacy mode settings"""
        try:
            # Disable camera if privacy mode is on
            if hasattr(self.controller.assistant, 'computer_vision'):
                self.controller.assistant.computer_vision.stop_camera()
            
            # Disable voice recording
            if hasattr(self.controller.assistant, 'voice_controller'):
                self.controller.assistant.voice_controller.stop_listening()
            
            # Enable data anonymization
            self.privacy_settings['anonymize_data'] = True
            
            self.logger.info("Privacy settings applied")
            
        except Exception as e:
            self.logger.error(f"Error applying privacy settings: {e}")
    
    def restore_normal_settings(self):
        """Restore normal operation settings"""
        try:
            # Re-enable camera
            if hasattr(self.controller.assistant, 'computer_vision'):
                self.controller.assistant.computer_vision.start_camera()
            
            # Re-enable voice recognition
            if hasattr(self.controller.assistant, 'voice_controller'):
                self.controller.assistant.voice_controller.start_listening()
            
            # Disable data anonymization
            self.privacy_settings['anonymize_data'] = False
            
            self.logger.info("Normal settings restored")
            
        except Exception as e:
            self.logger.error(f"Error restoring normal settings: {e}")
    
    def anonymize_data(self, data: Dict) -> Dict:
        """Anonymize sensitive data"""
        try:
            if not self.privacy_settings['anonymize_data']:
                return data
            
            anonymized = data.copy()
            
            # Remove or hash sensitive fields
            sensitive_fields = ['username', 'email', 'ip_address', 'location']
            
            for field in sensitive_fields:
                if field in anonymized:
                    if isinstance(anonymized[field], str):
                        anonymized[field] = hashlib.sha256(anonymized[field].encode()).hexdigest()[:8]
            
            return anonymized
            
        except Exception as e:
            self.logger.error(f"Error anonymizing data: {e}")
            return data
    
    def delete_old_logs(self, days: int = 30):
        """Delete logs older than specified days"""
        try:
            cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
            
            conn = sqlite3.connect(self.controller.db_path)
            cursor = conn.cursor()
            
            # Delete old security events
            cursor.execute('DELETE FROM security_events WHERE created_at < ?', (cutoff_date,))
            
            # Delete old access logs
            cursor.execute('DELETE FROM access_logs WHERE created_at < ?', (cutoff_date,))
            
            # Delete old sessions
            cursor.execute('DELETE FROM sessions WHERE created_at < ?', (cutoff_date,))
            
            conn.commit()
            conn.close()
            
            self.logger.info(f"Deleted logs older than {days} days")
            
        except Exception as e:
            self.logger.error(f"Error deleting old logs: {e}")


class AccessControl:
    """Access control and permissions management"""
    
    def __init__(self, security_controller):
        self.controller = security_controller
        self.logger = logging.getLogger(self.__class__.__name__)
        
        self.permissions = {
            'admin': ['all'],
            'user': ['basic_features', 'voice_control', 'entertainment'],
            'guest': ['basic_features']
        }
    
    def check_permission(self, user_role: str, resource: str) -> bool:
        """Check if user has permission for resource"""
        try:
            if user_role not in self.permissions:
                return False
            
            user_permissions = self.permissions[user_role]
            
            if 'all' in user_permissions:
                return True
            
            return resource in user_permissions
            
        except Exception as e:
            self.logger.error(f"Error checking permission: {e}")
            return False
    
    def log_access_attempt(self, user_id: Optional[int], resource: str, 
                          action: str, result: str):
        """Log access attempt"""
        try:
            conn = sqlite3.connect(self.controller.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO access_logs (user_id, resource, action, result, created_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, resource, action, result, datetime.now().isoformat()))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error logging access attempt: {e}")


class SecurityMonitor:
    """Security monitoring and threat detection"""
    
    def __init__(self, security_controller):
        self.controller = security_controller
        self.logger = logging.getLogger(self.__class__.__name__)
        
        self.monitoring_active = False
        self.threat_patterns = [
            'multiple_failed_logins',
            'unusual_access_patterns',
            'suspicious_commands',
            'unauthorized_access_attempts'
        ]
    
    def start_monitoring(self):
        """Start security monitoring"""
        self.monitoring_active = True
        threading.Thread(target=self._monitoring_loop, daemon=True).start()
        self.logger.info("Security monitoring started")
    
    def _monitoring_loop(self):
        """Main security monitoring loop"""
        while self.monitoring_active:
            try:
                # Check for security threats
                self._check_failed_login_attempts()
                self._check_unusual_activity()
                self._check_system_integrity()
                
                time.sleep(60)  # Check every minute
                
            except Exception as e:
                self.logger.error(f"Error in security monitoring: {e}")
                time.sleep(60)
    
    def _check_failed_login_attempts(self):
        """Check for excessive failed login attempts"""
        try:
            # Check last hour for failed attempts
            hour_ago = (datetime.now() - timedelta(hours=1)).isoformat()
            
            conn = sqlite3.connect(self.controller.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT COUNT(*) FROM security_events 
                WHERE event_type = 'authentication_failure' AND created_at >= ?
            ''', (hour_ago,))
            
            failed_attempts = cursor.fetchone()[0]
            conn.close()
            
            if failed_attempts > 10:  # Threshold for suspicious activity
                self.controller.log_security_event(
                    "suspicious_activity",
                    None,
                    f"Excessive failed login attempts: {failed_attempts}",
                    "warning"
                )
                
        except Exception as e:
            self.logger.error(f"Error checking failed login attempts: {e}")
    
    def _check_unusual_activity(self):
        """Check for unusual user activity patterns"""
        try:
            # This would implement more sophisticated anomaly detection
            # For now, it's a placeholder
            pass
        except Exception as e:
            self.logger.error(f"Error checking unusual activity: {e}")
    
    def _check_system_integrity(self):
        """Check system integrity"""
        try:
            # Check for unauthorized file modifications
            # Check for suspicious processes
            # Verify system configuration
            pass
        except Exception as e:
            self.logger.error(f"Error checking system integrity: {e}")


class BiometricAuthentication:
    """Biometric authentication using face recognition"""
    
    def __init__(self, security_controller):
        self.controller = security_controller
        self.logger = logging.getLogger(self.__class__.__name__)
        
        self.face_cascade = None
        self.face_recognizer = None
        self.known_faces = {}
        
        # Initialize face recognition
        self._initialize_face_recognition()
    
    def _initialize_face_recognition(self):
        """Initialize face recognition components"""
        try:
            # Load face cascade
            self.face_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            )
            
            # Initialize face recognizer
            self.face_recognizer = cv2.face.LBPHFaceRecognizer_create()
            
            # Load known faces
            self._load_known_faces()
            
        except Exception as e:
            self.logger.error(f"Error initializing face recognition: {e}")
    
    def is_available(self) -> bool:
        """Check if biometric authentication is available"""
        return (self.face_cascade is not None and 
                hasattr(self.controller.assistant, 'computer_vision') and
                self.controller.assistant.computer_vision.camera_active)
    
    def setup_face_recognition(self, user_id: int = None) -> bool:
        """Setup face recognition for user"""
        try:
            if not self.is_available():
                return False
            
            # Capture face samples
            face_samples = self._capture_face_samples()
            
            if len(face_samples) < 5:  # Need at least 5 samples
                self.logger.error("Insufficient face samples captured")
                return False
            
            # Train face recognizer
            if user_id is None and self.controller.authenticated_user:
                user_id = self.controller.authenticated_user['id']
            
            if user_id:
                self._train_face_recognizer(user_id, face_samples)
                self._save_biometric_data(user_id, 'face', face_samples)
                
                self.logger.info(f"Face recognition setup for user {user_id}")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error setting up face recognition: {e}")
            return False
    
    def authenticate_face(self) -> bool:
        """Authenticate user using face recognition"""
        try:
            if not self.is_available():
                return False
            
            # Capture current face
            current_frame = self.controller.assistant.computer_vision.current_frame
            
            if current_frame is None:
                return False
            
            # Detect faces
            gray = cv2.cvtColor(current_frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, 1.1, 5)
            
            if len(faces) == 0:
                return False
            
            # Use the largest face
            (x, y, w, h) = max(faces, key=lambda face: face[2] * face[3])
            face_roi = gray[y:y+h, x:x+w]
            
            # Recognize face
            if self.face_recognizer:
                user_id, confidence = self.face_recognizer.predict(face_roi)
                
                # Check confidence threshold
                if confidence < 100:  # Lower is better for LBPH
                    # Authenticate user
                    user = self._get_user_by_id(user_id)
                    if user:
                        self.controller.authenticated_user = user
                        self.controller.log_security_event(
                            "biometric_authentication_success",
                            user_id,
                            "Face recognition authentication successful"
                        )
                        return True
            
            self.controller.log_security_event(
                "biometric_authentication_failure",
                None,
                "Face recognition authentication failed"
            )
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error in face authentication: {e}")
            return False
    
    def _capture_face_samples(self, num_samples: int = 10) -> List[np.ndarray]:
        """Capture face samples for training"""
        try:
            samples = []
            
            if not hasattr(self.controller.assistant, 'computer_vision'):
                return samples
            
            cv_controller = self.controller.assistant.computer_vision
            
            for i in range(num_samples):
                # Get current frame
                current_frame = cv_controller.current_frame
                
                if current_frame is None:
                    time.sleep(0.5)
                    continue
                
                # Convert to grayscale
                gray = cv2.cvtColor(current_frame, cv2.COLOR_BGR2GRAY)
                
                # Detect faces
                faces = self.face_cascade.detectMultiScale(gray, 1.1, 5)
                
                if len(faces) > 0:
                    # Use the largest face
                    (x, y, w, h) = max(faces, key=lambda face: face[2] * face[3])
                    face_roi = gray[y:y+h, x:x+w]
                    
                    # Resize to standard size
                    face_roi = cv2.resize(face_roi, (200, 200))
                    samples.append(face_roi)
                
                time.sleep(0.5)  # Wait between captures
            
            return samples
            
        except Exception as e:
            self.logger.error(f"Error capturing face samples: {e}")
            return []
    
    def _train_face_recognizer(self, user_id: int, face_samples: List[np.ndarray]):
        """Train face recognizer with samples"""
        try:
            if not face_samples:
                return
            
            # Prepare training data
            faces = face_samples
            labels = [user_id] * len(face_samples)
            
            # Train recognizer
            self.face_recognizer.train(faces, np.array(labels))
            
            # Save trained model
            model_path = DATA_DIR / f"face_model_{user_id}.yml"
            self.face_recognizer.save(str(model_path))
            
        except Exception as e:
            self.logger.error(f"Error training face recognizer: {e}")
    
    def _save_biometric_data(self, user_id: int, biometric_type: str, data: List[np.ndarray]):
        """Save biometric data to database"""
        try:
            # Create hash of biometric data for storage
            data_hash = hashlib.sha256(str(data).encode()).hexdigest()
            
            conn = sqlite3.connect(self.controller.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO biometric_data (user_id, biometric_type, data_hash, created_at)
                VALUES (?, ?, ?, ?)
            ''', (user_id, biometric_type, data_hash, datetime.now().isoformat()))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error saving biometric data: {e}")
    
    def _load_known_faces(self):
        """Load known face data"""
        try:
            # Load face models for all users
            for model_file in DATA_DIR.glob("face_model_*.yml"):
                user_id = int(model_file.stem.split('_')[-1])
                
                recognizer = cv2.face.LBPHFaceRecognizer_create()
                recognizer.read(str(model_file))
                
                self.known_faces[user_id] = recognizer
            
        except Exception as e:
            self.logger.error(f"Error loading known faces: {e}")
    
    def _get_user_by_id(self, user_id: int) -> Optional[Dict]:
        """Get user information by ID"""
        try:
            conn = sqlite3.connect(self.controller.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, username, email, role FROM users WHERE id = ?
            ''', (user_id,))
            
            user_data = cursor.fetchone()
            conn.close()
            
            if user_data:
                return {
                    'id': user_data[0],
                    'username': user_data[1],
                    'email': user_data[2],
                    'role': user_data[3]
                }
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting user by ID: {e}")
            return None


class SessionManager:
    """Session management and cleanup"""
    
    def __init__(self, security_controller):
        self.controller = security_controller
        self.logger = logging.getLogger(self.__class__.__name__)
        
        self.current_session_id = None
        self.cleanup_active = False
    
    def create_session(self, user_id: int) -> str:
        """Create new session"""
        try:
            session_id = hashlib.sha256(f"{user_id}_{time.time()}".encode()).hexdigest()
            expires_at = (datetime.now() + timedelta(minutes=SECURITY_CONFIG["session_timeout"])).isoformat()
            
            conn = sqlite3.connect(self.controller.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO sessions (session_id, user_id, created_at, expires_at, last_activity)
                VALUES (?, ?, ?, ?, ?)
            ''', (session_id, user_id, datetime.now().isoformat(), expires_at, datetime.now().isoformat()))
            
            conn.commit()
            conn.close()
            
            self.current_session_id = session_id
            self.logger.info(f"Session created: {session_id}")
            
            return session_id
            
        except Exception as e:
            self.logger.error(f"Error creating session: {e}")
            return ""
    
    def end_current_session(self):
        """End current session"""
        try:
            if not self.current_session_id:
                return
            
            conn = sqlite3.connect(self.controller.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE sessions SET is_active = 0 WHERE session_id = ?
            ''', (self.current_session_id,))
            
            conn.commit()
            conn.close()
            
            self.logger.info(f"Session ended: {self.current_session_id}")
            self.current_session_id = None
            
        except Exception as e:
            self.logger.error(f"Error ending session: {e}")
    
    def has_active_session(self) -> bool:
        """Check if there's an active session"""
        return self.current_session_id is not None
    
    def start_session_cleanup(self):
        """Start session cleanup service"""
        self.cleanup_active = True
        threading.Thread(target=self._cleanup_loop, daemon=True).start()
    
    def _cleanup_loop(self):
        """Session cleanup loop"""
        while self.cleanup_active:
            try:
                # Clean up expired sessions
                current_time = datetime.now().isoformat()
                
                conn = sqlite3.connect(self.controller.db_path)
                cursor = conn.cursor()
                
                cursor.execute('''
                    UPDATE sessions SET is_active = 0 
                    WHERE expires_at < ? AND is_active = 1
                ''', (current_time,))
                
                conn.commit()
                conn.close()
                
                time.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                self.logger.error(f"Error in session cleanup: {e}")
                time.sleep(300)