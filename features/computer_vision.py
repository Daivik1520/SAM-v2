"""
Enhanced SAM AI Assistant - Computer Vision Module
"""
import cv2
import numpy as np
import threading
import time
import logging
from typing import Dict, List, Tuple, Optional, Callable
import mediapipe as mp
from datetime import datetime
import json

from core.base_assistant import BaseAssistant
from config.settings import CV_CONFIG

class ComputerVisionController:
    """Advanced computer vision with multiple detection capabilities"""
    
    def __init__(self, assistant: BaseAssistant):
        self.assistant = assistant
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Camera setup
        self.camera = None
        self.camera_active = False
        self.current_frame = None
        
        # MediaPipe setup
        self.mp_hands = mp.solutions.hands
        self.mp_pose = mp.solutions.pose
        self.mp_face_mesh = mp.solutions.face_mesh
        self.mp_drawing = mp.solutions.drawing_utils
        
        # Detection models
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
        
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
        
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
        
        # Face detection
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        
        # Object detection (simplified - would use YOLO or similar)
        self.object_classes = [
            'person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus',
            'train', 'truck', 'boat', 'traffic light', 'fire hydrant',
            'stop sign', 'parking meter', 'bench', 'bird', 'cat', 'dog',
            'horse', 'sheep', 'cow', 'elephant', 'bear', 'zebra', 'giraffe',
            'backpack', 'umbrella', 'handbag', 'tie', 'suitcase', 'frisbee',
            'skis', 'snowboard', 'sports ball', 'kite', 'baseball bat',
            'baseball glove', 'skateboard', 'surfboard', 'tennis racket',
            'bottle', 'wine glass', 'cup', 'fork', 'knife', 'spoon', 'bowl',
            'banana', 'apple', 'sandwich', 'orange', 'broccoli', 'carrot',
            'hot dog', 'pizza', 'donut', 'cake', 'chair', 'couch',
            'potted plant', 'bed', 'dining table', 'toilet', 'tv', 'laptop',
            'mouse', 'remote', 'keyboard', 'cell phone', 'microwave',
            'oven', 'toaster', 'sink', 'refrigerator', 'book', 'clock',
            'vase', 'scissors', 'teddy bear', 'hair drier', 'toothbrush'
        ]
        
        # Detection callbacks
        self.detection_callbacks: Dict[str, List[Callable]] = {
            'face_detected': [],
            'gesture_detected': [],
            'object_detected': [],
            'emotion_detected': [],
            'pose_detected': []
        }
        
        # Gesture recognition
        self.gesture_history = []
        self.gesture_commands = {
            'thumbs_up': self.handle_thumbs_up,
            'peace_sign': self.handle_peace_sign,
            'pointing': self.handle_pointing,
            'wave': self.handle_wave,
            'fist': self.handle_fist
        }
        
        # Emotion detection (simplified)
        self.emotion_labels = ['angry', 'disgust', 'fear', 'happy', 'sad', 'surprise', 'neutral']
        
        # Tracking data
        self.tracking_data = {
            'faces': [],
            'hands': [],
            'poses': [],
            'objects': [],
            'emotions': []
        }
        
        # Performance monitoring
        self.fps_counter = 0
        self.fps_start_time = time.time()
        self.current_fps = 0
        
    def start_camera(self, camera_index: int = None) -> bool:
        """Start camera capture"""
        try:
            if camera_index is None:
                camera_index = CV_CONFIG["camera_index"]
            
            self.camera = cv2.VideoCapture(camera_index)
            
            if not self.camera.isOpened():
                self.logger.error(f"Failed to open camera {camera_index}")
                return False
            
            # Set camera properties
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
            self.camera.set(cv2.CAP_PROP_FPS, 30)
            
            self.camera_active = True
            
            # Start processing thread
            self.processing_thread = threading.Thread(target=self._process_video, daemon=True)
            self.processing_thread.start()
            
            self.logger.info("Camera started successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error starting camera: {e}")
            return False
    
    def stop_camera(self):
        """Stop camera capture"""
        self.camera_active = False
        
        if self.camera:
            self.camera.release()
            self.camera = None
        
        self.logger.info("Camera stopped")
    
    def _process_video(self):
        """Main video processing loop"""
        while self.camera_active and self.camera:
            try:
                ret, frame = self.camera.read()
                if not ret:
                    continue
                
                self.current_frame = frame.copy()
                
                # Flip frame horizontally for mirror effect
                frame = cv2.flip(frame, 1)
                
                # Convert BGR to RGB for MediaPipe
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Process detections
                self._detect_faces(frame)
                self._detect_hands(rgb_frame, frame)
                self._detect_pose(rgb_frame, frame)
                self._detect_emotions(frame)
                
                # Update FPS
                self._update_fps()
                
                # Add FPS to frame
                cv2.putText(frame, f"FPS: {self.current_fps:.1f}", 
                           (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                
                # Display frame (optional - for debugging)
                if CV_CONFIG.get("show_video", False):
                    cv2.imshow("SAM Vision", frame)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
                
                time.sleep(0.01)  # Small delay to prevent excessive CPU usage
                
            except Exception as e:
                self.logger.error(f"Error in video processing: {e}")
                time.sleep(0.1)
    
    def _detect_faces(self, frame):
        """Detect faces in frame"""
        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(
                gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
            )
            
            current_faces = []
            
            for (x, y, w, h) in faces:
                face_data = {
                    'bbox': (x, y, w, h),
                    'center': (x + w//2, y + h//2),
                    'area': w * h,
                    'timestamp': time.time()
                }
                
                current_faces.append(face_data)
                
                # Draw rectangle around face
                cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
                cv2.putText(frame, "Face", (x, y-10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 0), 2)
            
            # Update tracking data
            self.tracking_data['faces'] = current_faces
            
            # Trigger callbacks
            if current_faces:
                self._trigger_callbacks('face_detected', current_faces)
                
        except Exception as e:
            self.logger.error(f"Error in face detection: {e}")
    
    def _detect_hands(self, rgb_frame, display_frame):
        """Detect hands and gestures"""
        try:
            results = self.hands.process(rgb_frame)
            
            current_hands = []
            
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    # Draw hand landmarks
                    self.mp_drawing.draw_landmarks(
                        display_frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS
                    )
                    
                    # Extract hand data
                    landmarks = []
                    for landmark in hand_landmarks.landmark:
                        landmarks.append([landmark.x, landmark.y, landmark.z])
                    
                    hand_data = {
                        'landmarks': landmarks,
                        'timestamp': time.time()
                    }
                    
                    current_hands.append(hand_data)
                    
                    # Recognize gestures
                    gesture = self._recognize_gesture(landmarks)
                    if gesture:
                        cv2.putText(display_frame, f"Gesture: {gesture}", 
                                   (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                        
                        if gesture in self.gesture_commands:
                            self.gesture_commands[gesture]()
            
            # Update tracking data
            self.tracking_data['hands'] = current_hands
            
            # Trigger callbacks
            if current_hands:
                self._trigger_callbacks('gesture_detected', current_hands)
                
        except Exception as e:
            self.logger.error(f"Error in hand detection: {e}")
    
    def _detect_pose(self, rgb_frame, display_frame):
        """Detect body pose"""
        try:
            results = self.pose.process(rgb_frame)
            
            if results.pose_landmarks:
                # Draw pose landmarks
                self.mp_drawing.draw_landmarks(
                    display_frame, results.pose_landmarks, self.mp_pose.POSE_CONNECTIONS
                )
                
                # Extract pose data
                landmarks = []
                for landmark in results.pose_landmarks.landmark:
                    landmarks.append([landmark.x, landmark.y, landmark.z, landmark.visibility])
                
                pose_data = {
                    'landmarks': landmarks,
                    'timestamp': time.time()
                }
                
                # Update tracking data
                self.tracking_data['poses'] = [pose_data]
                
                # Analyze pose
                pose_analysis = self._analyze_pose(landmarks)
                if pose_analysis:
                    cv2.putText(display_frame, f"Pose: {pose_analysis}", 
                               (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
                
                # Trigger callbacks
                self._trigger_callbacks('pose_detected', pose_data)
                
        except Exception as e:
            self.logger.error(f"Error in pose detection: {e}")
    
    def _detect_emotions(self, frame):
        """Detect emotions from facial expressions"""
        try:
            # Simplified emotion detection
            # In a real implementation, you'd use a trained emotion recognition model
            
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, 1.1, 5)
            
            for (x, y, w, h) in faces:
                face_roi = gray[y:y+h, x:x+w]
                
                # Placeholder emotion detection
                # This would be replaced with actual emotion recognition
                emotion = self._analyze_facial_expression(face_roi)
                
                if emotion:
                    cv2.putText(frame, f"Emotion: {emotion}", 
                               (x, y-30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                    
                    emotion_data = {
                        'emotion': emotion,
                        'confidence': 0.8,  # Placeholder
                        'bbox': (x, y, w, h),
                        'timestamp': time.time()
                    }
                    
                    self.tracking_data['emotions'] = [emotion_data]
                    self._trigger_callbacks('emotion_detected', emotion_data)
                
        except Exception as e:
            self.logger.error(f"Error in emotion detection: {e}")
    
    def _recognize_gesture(self, landmarks) -> Optional[str]:
        """Recognize hand gestures from landmarks"""
        try:
            # Simplified gesture recognition
            # This would be more sophisticated in a real implementation
            
            # Get key points
            thumb_tip = landmarks[4]
            thumb_ip = landmarks[3]
            index_tip = landmarks[8]
            index_pip = landmarks[6]
            middle_tip = landmarks[12]
            ring_tip = landmarks[16]
            pinky_tip = landmarks[20]
            
            # Thumbs up detection
            if (thumb_tip[1] < thumb_ip[1] and 
                index_tip[1] > index_pip[1] and
                middle_tip[1] > landmarks[10][1]):
                return "thumbs_up"
            
            # Peace sign detection
            if (index_tip[1] < index_pip[1] and 
                middle_tip[1] < landmarks[10][1] and
                ring_tip[1] > landmarks[14][1] and
                pinky_tip[1] > landmarks[18][1]):
                return "peace_sign"
            
            # Pointing detection
            if (index_tip[1] < index_pip[1] and
                middle_tip[1] > landmarks[10][1] and
                ring_tip[1] > landmarks[14][1] and
                pinky_tip[1] > landmarks[18][1]):
                return "pointing"
            
            # Fist detection
            if (all(tip[1] > pip[1] for tip, pip in [
                (index_tip, index_pip),
                (middle_tip, landmarks[10]),
                (ring_tip, landmarks[14]),
                (pinky_tip, landmarks[18])
            ])):
                return "fist"
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error recognizing gesture: {e}")
            return None
    
    def _analyze_pose(self, landmarks) -> Optional[str]:
        """Analyze body pose"""
        try:
            # Simplified pose analysis
            # Get key body points
            left_shoulder = landmarks[11]
            right_shoulder = landmarks[12]
            left_elbow = landmarks[13]
            right_elbow = landmarks[14]
            left_wrist = landmarks[15]
            right_wrist = landmarks[16]
            
            # Check if arms are raised
            if (left_wrist[1] < left_shoulder[1] and 
                right_wrist[1] < right_shoulder[1]):
                return "arms_raised"
            
            # Check if person is sitting
            left_hip = landmarks[23]
            right_hip = landmarks[24]
            left_knee = landmarks[25]
            right_knee = landmarks[26]
            
            if (left_knee[1] > left_hip[1] and 
                right_knee[1] > right_hip[1]):
                return "sitting"
            
            return "standing"
            
        except Exception as e:
            self.logger.error(f"Error analyzing pose: {e}")
            return None
    
    def _analyze_facial_expression(self, face_roi) -> Optional[str]:
        """Analyze facial expression for emotion"""
        try:
            # Placeholder emotion analysis
            # In reality, this would use a trained emotion recognition model
            
            # Simple analysis based on face region properties
            height, width = face_roi.shape
            
            # Analyze different regions of the face
            upper_face = face_roi[:height//2, :]
            lower_face = face_roi[height//2:, :]
            
            # Calculate some basic features
            upper_mean = np.mean(upper_face)
            lower_mean = np.mean(lower_face)
            
            # Very simplified emotion detection
            if upper_mean > lower_mean + 10:
                return "happy"
            elif lower_mean > upper_mean + 10:
                return "sad"
            else:
                return "neutral"
                
        except Exception as e:
            self.logger.error(f"Error analyzing facial expression: {e}")
            return None
    
    def _update_fps(self):
        """Update FPS counter"""
        self.fps_counter += 1
        current_time = time.time()
        
        if current_time - self.fps_start_time >= 1.0:
            self.current_fps = self.fps_counter / (current_time - self.fps_start_time)
            self.fps_counter = 0
            self.fps_start_time = current_time
    
    def _trigger_callbacks(self, event: str, data):
        """Trigger registered callbacks for detection events"""
        if event in self.detection_callbacks:
            for callback in self.detection_callbacks[event]:
                try:
                    callback(data)
                except Exception as e:
                    self.logger.error(f"Error in detection callback: {e}")
    
    def register_detection_callback(self, event: str, callback: Callable):
        """Register callback for detection events"""
        if event not in self.detection_callbacks:
            self.detection_callbacks[event] = []
        self.detection_callbacks[event].append(callback)
    
    # Gesture command handlers
    def handle_thumbs_up(self):
        """Handle thumbs up gesture"""
        self.assistant.emit_event("gesture_command", {"gesture": "thumbs_up", "action": "approve"})
    
    def handle_peace_sign(self):
        """Handle peace sign gesture"""
        self.assistant.emit_event("gesture_command", {"gesture": "peace_sign", "action": "peace"})
    
    def handle_pointing(self):
        """Handle pointing gesture"""
        self.assistant.emit_event("gesture_command", {"gesture": "pointing", "action": "select"})
    
    def handle_wave(self):
        """Handle wave gesture"""
        self.assistant.emit_event("gesture_command", {"gesture": "wave", "action": "hello"})
    
    def handle_fist(self):
        """Handle fist gesture"""
        self.assistant.emit_event("gesture_command", {"gesture": "fist", "action": "stop"})
    
    def take_screenshot(self) -> Optional[np.ndarray]:
        """Take screenshot of current frame"""
        if self.current_frame is not None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}.jpg"
            filepath = CV_CONFIG.get("screenshot_dir", "screenshots") + "/" + filename
            
            cv2.imwrite(filepath, self.current_frame)
            self.logger.info(f"Screenshot saved: {filepath}")
            
            return self.current_frame.copy()
        
        return None
    
    def start_recording(self, duration: int = 30):
        """Start video recording"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"recording_{timestamp}.mp4"
            filepath = CV_CONFIG.get("recording_dir", "recordings") + "/" + filename
            
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(filepath, fourcc, 20.0, (1280, 720))
            
            start_time = time.time()
            
            while time.time() - start_time < duration and self.camera_active:
                if self.current_frame is not None:
                    out.write(self.current_frame)
                time.sleep(0.05)
            
            out.release()
            self.logger.info(f"Recording saved: {filepath}")
            
        except Exception as e:
            self.logger.error(f"Error recording video: {e}")
    
    def get_vision_stats(self) -> Dict:
        """Get computer vision statistics"""
        return {
            "camera_active": self.camera_active,
            "current_fps": self.current_fps,
            "faces_detected": len(self.tracking_data['faces']),
            "hands_detected": len(self.tracking_data['hands']),
            "poses_detected": len(self.tracking_data['poses']),
            "emotions_detected": len(self.tracking_data['emotions']),
            "tracking_data": self.tracking_data
        }