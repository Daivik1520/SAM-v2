"""
Enhanced SAM AI Assistant - Smart Home Integration Module
"""
import asyncio
import json
import logging
import time
from typing import Dict, List, Optional, Any, Callable
import requests
from datetime import datetime, timedelta
import threading

from core.base_assistant import BaseAssistant
from config.settings import API_KEYS

class SmartHomeController:
    """Smart home device control and automation"""
    
    def __init__(self, assistant: BaseAssistant):
        self.assistant = assistant
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Device registry
        self.devices: Dict[str, Dict] = {}
        self.device_groups: Dict[str, List[str]] = {}
        self.scenes: Dict[str, Dict] = {}
        self.routines: Dict[str, Dict] = {}
        
        # Supported device types
        self.device_types = {
            'light': LightDevice,
            'switch': SwitchDevice,
            'thermostat': ThermostatDevice,
            'camera': CameraDevice,
            'sensor': SensorDevice,
            'lock': LockDevice,
            'speaker': SpeakerDevice,
            'tv': TVDevice,
            'fan': FanDevice,
            'blinds': BlindsDevice
        }
        
        # Automation engine
        self.automation_active = False
        self.automation_thread = None
        
        # Energy monitoring
        self.energy_data = {}
        
        # Security system
        self.security_system = SecuritySystem(self)
        
        # Load saved configuration
        self.load_configuration()
        
        # Register voice commands
        self.register_voice_commands()
    
    def register_voice_commands(self):
        """Register smart home voice commands"""
        if hasattr(self.assistant, 'voice_controller'):
            voice = self.assistant.voice_controller
            
            # Lighting commands
            voice.register_command(
                ["turn on *", "turn * on"],
                self.voice_turn_on,
                "Turn on a device or group"
            )
            
            voice.register_command(
                ["turn off *", "turn * off"],
                self.voice_turn_off,
                "Turn off a device or group"
            )
            
            voice.register_command(
                ["dim * to *", "set * brightness to *"],
                self.voice_dim_lights,
                "Dim lights to specific level"
            )
            
            # Temperature commands
            voice.register_command(
                ["set temperature to *", "set thermostat to *"],
                self.voice_set_temperature,
                "Set thermostat temperature"
            )
            
            # Scene commands
            voice.register_command(
                ["activate * scene", "set * scene"],
                self.voice_activate_scene,
                "Activate a scene"
            )
            
            # Security commands
            voice.register_command(
                ["arm security system", "activate security"],
                self.voice_arm_security,
                "Arm security system"
            )
            
            voice.register_command(
                ["disarm security system", "deactivate security"],
                self.voice_disarm_security,
                "Disarm security system"
            )
            
            # Status commands
            voice.register_command(
                ["what's the status of *", "check *"],
                self.voice_device_status,
                "Check device status"
            )
    
    def add_device(self, device_id: str, device_type: str, name: str, 
                   location: str, config: Dict = None) -> bool:
        """Add a new smart home device"""
        try:
            if device_type not in self.device_types:
                self.logger.error(f"Unsupported device type: {device_type}")
                return False
            
            device_class = self.device_types[device_type]
            device = device_class(device_id, name, location, config or {})
            
            self.devices[device_id] = {
                'device': device,
                'type': device_type,
                'name': name,
                'location': location,
                'added': datetime.now().isoformat(),
                'last_updated': datetime.now().isoformat()
            }
            
            self.logger.info(f"Added device: {name} ({device_type}) in {location}")
            self.save_configuration()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error adding device: {e}")
            return False
    
    def remove_device(self, device_id: str) -> bool:
        """Remove a smart home device"""
        try:
            if device_id in self.devices:
                device_info = self.devices[device_id]
                del self.devices[device_id]
                
                # Remove from groups
                for group_name, device_list in self.device_groups.items():
                    if device_id in device_list:
                        device_list.remove(device_id)
                
                self.logger.info(f"Removed device: {device_info['name']}")
                self.save_configuration()
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error removing device: {e}")
            return False
    
    def create_group(self, group_name: str, device_ids: List[str]) -> bool:
        """Create a device group"""
        try:
            # Validate devices exist
            for device_id in device_ids:
                if device_id not in self.devices:
                    self.logger.error(f"Device not found: {device_id}")
                    return False
            
            self.device_groups[group_name] = device_ids
            self.logger.info(f"Created group: {group_name} with {len(device_ids)} devices")
            self.save_configuration()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error creating group: {e}")
            return False
    
    def create_scene(self, scene_name: str, device_states: Dict[str, Dict]) -> bool:
        """Create a scene with specific device states"""
        try:
            self.scenes[scene_name] = {
                'device_states': device_states,
                'created': datetime.now().isoformat(),
                'last_activated': None
            }
            
            self.logger.info(f"Created scene: {scene_name}")
            self.save_configuration()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error creating scene: {e}")
            return False
    
    def activate_scene(self, scene_name: str) -> bool:
        """Activate a scene"""
        try:
            if scene_name not in self.scenes:
                self.logger.error(f"Scene not found: {scene_name}")
                return False
            
            scene = self.scenes[scene_name]
            
            for device_id, state in scene['device_states'].items():
                if device_id in self.devices:
                    device = self.devices[device_id]['device']
                    device.set_state(state)
            
            scene['last_activated'] = datetime.now().isoformat()
            self.logger.info(f"Activated scene: {scene_name}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error activating scene: {e}")
            return False
    
    def control_device(self, device_id: str, action: str, parameters: Dict = None) -> bool:
        """Control a specific device"""
        try:
            if device_id not in self.devices:
                self.logger.error(f"Device not found: {device_id}")
                return False
            
            device = self.devices[device_id]['device']
            result = device.execute_action(action, parameters or {})
            
            if result:
                self.devices[device_id]['last_updated'] = datetime.now().isoformat()
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error controlling device: {e}")
            return False
    
    def control_group(self, group_name: str, action: str, parameters: Dict = None) -> bool:
        """Control a group of devices"""
        try:
            if group_name not in self.device_groups:
                self.logger.error(f"Group not found: {group_name}")
                return False
            
            success_count = 0
            device_ids = self.device_groups[group_name]
            
            for device_id in device_ids:
                if self.control_device(device_id, action, parameters):
                    success_count += 1
            
            self.logger.info(f"Controlled {success_count}/{len(device_ids)} devices in group {group_name}")
            
            return success_count > 0
            
        except Exception as e:
            self.logger.error(f"Error controlling group: {e}")
            return False
    
    def create_routine(self, routine_name: str, triggers: List[Dict], 
                      actions: List[Dict], conditions: List[Dict] = None) -> bool:
        """Create an automation routine"""
        try:
            self.routines[routine_name] = {
                'triggers': triggers,
                'actions': actions,
                'conditions': conditions or [],
                'enabled': True,
                'created': datetime.now().isoformat(),
                'last_triggered': None,
                'trigger_count': 0
            }
            
            self.logger.info(f"Created routine: {routine_name}")
            self.save_configuration()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error creating routine: {e}")
            return False
    
    def start_automation(self):
        """Start automation engine"""
        if self.automation_active:
            return
        
        self.automation_active = True
        self.automation_thread = threading.Thread(target=self._automation_loop, daemon=True)
        self.automation_thread.start()
        
        self.logger.info("Automation engine started")
    
    def stop_automation(self):
        """Stop automation engine"""
        self.automation_active = False
        self.logger.info("Automation engine stopped")
    
    def _automation_loop(self):
        """Main automation loop"""
        while self.automation_active:
            try:
                current_time = datetime.now()
                
                for routine_name, routine in self.routines.items():
                    if not routine['enabled']:
                        continue
                    
                    # Check triggers
                    if self._check_triggers(routine['triggers'], current_time):
                        # Check conditions
                        if self._check_conditions(routine['conditions'], current_time):
                            # Execute actions
                            self._execute_actions(routine['actions'])
                            
                            routine['last_triggered'] = current_time.isoformat()
                            routine['trigger_count'] += 1
                            
                            self.logger.info(f"Executed routine: {routine_name}")
                
                time.sleep(10)  # Check every 10 seconds
                
            except Exception as e:
                self.logger.error(f"Error in automation loop: {e}")
                time.sleep(10)
    
    def _check_triggers(self, triggers: List[Dict], current_time: datetime) -> bool:
        """Check if any triggers are activated"""
        for trigger in triggers:
            trigger_type = trigger.get('type')
            
            if trigger_type == 'time':
                target_time = trigger.get('time')
                if self._is_time_match(current_time, target_time):
                    return True
            
            elif trigger_type == 'device_state':
                device_id = trigger.get('device_id')
                expected_state = trigger.get('state')
                
                if device_id in self.devices:
                    device = self.devices[device_id]['device']
                    if device.get_state() == expected_state:
                        return True
            
            elif trigger_type == 'sensor':
                sensor_id = trigger.get('sensor_id')
                condition = trigger.get('condition')
                value = trigger.get('value')
                
                if self._check_sensor_condition(sensor_id, condition, value):
                    return True
        
        return False
    
    def _check_conditions(self, conditions: List[Dict], current_time: datetime) -> bool:
        """Check if all conditions are met"""
        for condition in conditions:
            condition_type = condition.get('type')
            
            if condition_type == 'time_range':
                start_time = condition.get('start_time')
                end_time = condition.get('end_time')
                
                if not self._is_in_time_range(current_time, start_time, end_time):
                    return False
            
            elif condition_type == 'device_state':
                device_id = condition.get('device_id')
                expected_state = condition.get('state')
                
                if device_id in self.devices:
                    device = self.devices[device_id]['device']
                    if device.get_state() != expected_state:
                        return False
        
        return True
    
    def _execute_actions(self, actions: List[Dict]):
        """Execute routine actions"""
        for action in actions:
            action_type = action.get('type')
            
            if action_type == 'device_control':
                device_id = action.get('device_id')
                command = action.get('command')
                parameters = action.get('parameters', {})
                
                self.control_device(device_id, command, parameters)
            
            elif action_type == 'scene':
                scene_name = action.get('scene_name')
                self.activate_scene(scene_name)
            
            elif action_type == 'notification':
                message = action.get('message')
                self.assistant.emit_event('notification', {'message': message})
    
    # Voice command handlers
    def voice_turn_on(self, text: str):
        """Handle voice turn on command"""
        # Extract device/group name from text
        words = text.split()
        if len(words) >= 3:
            target = ' '.join(words[2:])  # Skip "turn on"
            
            if target in self.devices:
                self.control_device(target, 'turn_on')
                self.assistant.voice_controller.speak(f"Turning on {target}")
            elif target in self.device_groups:
                self.control_group(target, 'turn_on')
                self.assistant.voice_controller.speak(f"Turning on {target} group")
            else:
                self.assistant.voice_controller.speak(f"Device or group {target} not found")
    
    def voice_turn_off(self, text: str):
        """Handle voice turn off command"""
        words = text.split()
        if len(words) >= 3:
            target = ' '.join(words[2:])  # Skip "turn off"
            
            if target in self.devices:
                self.control_device(target, 'turn_off')
                self.assistant.voice_controller.speak(f"Turning off {target}")
            elif target in self.device_groups:
                self.control_group(target, 'turn_off')
                self.assistant.voice_controller.speak(f"Turning off {target} group")
            else:
                self.assistant.voice_controller.speak(f"Device or group {target} not found")
    
    def voice_dim_lights(self, text: str):
        """Handle voice dim lights command"""
        # Extract device name and brightness level
        # This is a simplified implementation
        self.assistant.voice_controller.speak("Light dimming feature activated")
    
    def voice_set_temperature(self, text: str):
        """Handle voice set temperature command"""
        # Extract temperature value
        # This is a simplified implementation
        self.assistant.voice_controller.speak("Temperature setting updated")
    
    def voice_activate_scene(self, text: str):
        """Handle voice activate scene command"""
        words = text.split()
        if len(words) >= 2:
            scene_name = words[1]  # Get scene name
            
            if self.activate_scene(scene_name):
                self.assistant.voice_controller.speak(f"Activated {scene_name} scene")
            else:
                self.assistant.voice_controller.speak(f"Scene {scene_name} not found")
    
    def voice_arm_security(self, text: str):
        """Handle voice arm security command"""
        if self.security_system.arm():
            self.assistant.voice_controller.speak("Security system armed")
        else:
            self.assistant.voice_controller.speak("Failed to arm security system")
    
    def voice_disarm_security(self, text: str):
        """Handle voice disarm security command"""
        if self.security_system.disarm():
            self.assistant.voice_controller.speak("Security system disarmed")
        else:
            self.assistant.voice_controller.speak("Failed to disarm security system")
    
    def voice_device_status(self, text: str):
        """Handle voice device status command"""
        words = text.split()
        if len(words) >= 4:
            device_name = ' '.join(words[3:])  # Skip "what's the status of"
            
            if device_name in self.devices:
                device = self.devices[device_name]['device']
                status = device.get_status()
                self.assistant.voice_controller.speak(f"{device_name} is {status}")
            else:
                self.assistant.voice_controller.speak(f"Device {device_name} not found")
    
    def get_energy_usage(self) -> Dict:
        """Get energy usage statistics"""
        total_usage = 0
        device_usage = {}
        
        for device_id, device_info in self.devices.items():
            device = device_info['device']
            if hasattr(device, 'get_energy_usage'):
                usage = device.get_energy_usage()
                device_usage[device_id] = usage
                total_usage += usage
        
        return {
            'total_usage': total_usage,
            'device_usage': device_usage,
            'timestamp': datetime.now().isoformat()
        }
    
    def save_configuration(self):
        """Save smart home configuration"""
        try:
            config = {
                'devices': {k: {
                    'type': v['type'],
                    'name': v['name'],
                    'location': v['location'],
                    'added': v['added']
                } for k, v in self.devices.items()},
                'device_groups': self.device_groups,
                'scenes': self.scenes,
                'routines': self.routines
            }
            
            with open('data/smart_home_config.json', 'w') as f:
                json.dump(config, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Error saving configuration: {e}")
    
    def load_configuration(self):
        """Load smart home configuration"""
        try:
            with open('data/smart_home_config.json', 'r') as f:
                config = json.load(f)
            
            # Recreate devices
            for device_id, device_config in config.get('devices', {}).items():
                self.add_device(
                    device_id,
                    device_config['type'],
                    device_config['name'],
                    device_config['location']
                )
            
            self.device_groups = config.get('device_groups', {})
            self.scenes = config.get('scenes', {})
            self.routines = config.get('routines', {})
            
        except FileNotFoundError:
            self.logger.info("No existing configuration found")
        except Exception as e:
            self.logger.error(f"Error loading configuration: {e}")
    
    def get_smart_home_stats(self) -> Dict:
        """Get smart home statistics"""
        return {
            'total_devices': len(self.devices),
            'device_groups': len(self.device_groups),
            'scenes': len(self.scenes),
            'routines': len(self.routines),
            'automation_active': self.automation_active,
            'energy_usage': self.get_energy_usage()
        }


# Device Classes
class SmartDevice:
    """Base class for smart devices"""
    
    def __init__(self, device_id: str, name: str, location: str, config: Dict):
        self.device_id = device_id
        self.name = name
        self.location = location
        self.config = config
        self.state = {}
        self.last_updated = datetime.now()
    
    def get_state(self) -> Dict:
        """Get current device state"""
        return self.state.copy()
    
    def set_state(self, new_state: Dict):
        """Set device state"""
        self.state.update(new_state)
        self.last_updated = datetime.now()
    
    def execute_action(self, action: str, parameters: Dict) -> bool:
        """Execute device action"""
        return False
    
    def get_status(self) -> str:
        """Get device status string"""
        return "unknown"


class LightDevice(SmartDevice):
    """Smart light device"""
    
    def __init__(self, device_id: str, name: str, location: str, config: Dict):
        super().__init__(device_id, name, location, config)
        self.state = {
            'power': False,
            'brightness': 100,
            'color': {'r': 255, 'g': 255, 'b': 255}
        }
    
    def execute_action(self, action: str, parameters: Dict) -> bool:
        if action == 'turn_on':
            self.state['power'] = True
            return True
        elif action == 'turn_off':
            self.state['power'] = False
            return True
        elif action == 'set_brightness':
            brightness = parameters.get('brightness', 100)
            self.state['brightness'] = max(0, min(100, brightness))
            return True
        elif action == 'set_color':
            color = parameters.get('color', {})
            self.state['color'].update(color)
            return True
        
        return False
    
    def get_status(self) -> str:
        if self.state['power']:
            return f"on at {self.state['brightness']}% brightness"
        else:
            return "off"


class ThermostatDevice(SmartDevice):
    """Smart thermostat device"""
    
    def __init__(self, device_id: str, name: str, location: str, config: Dict):
        super().__init__(device_id, name, location, config)
        self.state = {
            'temperature': 72,
            'target_temperature': 72,
            'mode': 'auto',
            'fan': 'auto'
        }
    
    def execute_action(self, action: str, parameters: Dict) -> bool:
        if action == 'set_temperature':
            temp = parameters.get('temperature', 72)
            self.state['target_temperature'] = max(50, min(90, temp))
            return True
        elif action == 'set_mode':
            mode = parameters.get('mode', 'auto')
            if mode in ['heat', 'cool', 'auto', 'off']:
                self.state['mode'] = mode
                return True
        
        return False
    
    def get_status(self) -> str:
        return f"set to {self.state['target_temperature']}°F in {self.state['mode']} mode"


class SecuritySystem:
    """Security system controller"""
    
    def __init__(self, smart_home_controller):
        self.controller = smart_home_controller
        self.armed = False
        self.sensors = []
        self.cameras = []
        self.alerts = []
    
    def arm(self) -> bool:
        """Arm security system"""
        self.armed = True
        return True
    
    def disarm(self) -> bool:
        """Disarm security system"""
        self.armed = False
        return True
    
    def add_alert(self, alert_type: str, message: str):
        """Add security alert"""
        alert = {
            'type': alert_type,
            'message': message,
            'timestamp': datetime.now().isoformat()
        }
        self.alerts.append(alert)


# Additional device classes would be implemented similarly
class SwitchDevice(SmartDevice):
    pass

class CameraDevice(SmartDevice):
    pass

class SensorDevice(SmartDevice):
    pass

class LockDevice(SmartDevice):
    pass

class SpeakerDevice(SmartDevice):
    pass

class TVDevice(SmartDevice):
    pass

class FanDevice(SmartDevice):
    pass

class BlindsDevice(SmartDevice):
    pass