"""
Data persistence module for the ASM Tournament Bot
Handles loading and saving of scheduled events, rules, and tour panel configurations
"""

import json
import os
import datetime

# File paths for persistent storage
SCHEDULED_EVENTS_FILE = 'scheduled_events.json'
RULES_FILE = 'tournament_rules.json'
TOUR_PANEL_CONFIG_FILE = 'tour_panel_config.json'

# Global storage
scheduled_events = {}
tournament_rules = {}

def load_scheduled_events():
    """Load scheduled events from file on startup"""
    global scheduled_events
    try:
        if os.path.exists(SCHEDULED_EVENTS_FILE):
            with open(SCHEDULED_EVENTS_FILE, 'r') as f:
                data = json.load(f)
                # Convert datetime strings back to datetime objects
                for event_id, event_data in data.items():
                    if 'datetime' in event_data:
                        event_data['datetime'] = datetime.datetime.fromisoformat(event_data['datetime'])
                scheduled_events = data
                print(f"Loaded {len(scheduled_events)} scheduled events from file")
    except Exception as e:
        print(f"Error loading scheduled events: {e}")
        scheduled_events = {}

def save_scheduled_events():
    """Save scheduled events to file"""
    try:
        # Convert datetime objects to strings for JSON serialization
        data_to_save = {}
        for event_id, event_data in scheduled_events.items():
            event_copy = event_data.copy()
            if 'datetime' in event_copy:
                event_copy['datetime'] = event_copy['datetime'].isoformat()
            # Remove non-serializable objects like discord.Member
            if 'judge' in event_copy:
                event_copy['judge'] = None
            data_to_save[event_id] = event_copy
        
        with open(SCHEDULED_EVENTS_FILE, 'w') as f:
            json.dump(data_to_save, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving scheduled events: {e}")
        return False

def load_tour_panel_config() -> dict:
    """Load tour panel configuration from file"""
    try:
        if os.path.exists(TOUR_PANEL_CONFIG_FILE):
            with open(TOUR_PANEL_CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading tour panel config: {e}")
    return {}

def save_tour_panel_config(config: dict) -> bool:
    """Save tour panel configuration to file"""
    try:
        with open(TOUR_PANEL_CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error saving tour panel config: {e}")
        return False

def load_rules():
    """Load tournament rules from persistent storage"""
    global tournament_rules
    try:
        if os.path.exists(RULES_FILE):
            with open(RULES_FILE, 'r', encoding='utf-8') as f:
                tournament_rules = json.load(f)
                print(f"Loaded tournament rules from file")
        else:
            tournament_rules = {}
            print("No existing rules file found, starting with empty rules")
    except Exception as e:
        print(f"Error loading tournament rules: {e}")
        tournament_rules = {}

def save_rules():
    """Save tournament rules to persistent storage"""
    try:
        with open(RULES_FILE, 'w', encoding='utf-8') as f:
            json.dump(tournament_rules, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error saving tournament rules: {e}")
        return False

def get_current_rules():
    """Get current rules content"""
    return tournament_rules.get('rules', {}).get('content', '')

def set_rules_content(content, user_id, username):
    """Set new rules content with metadata"""
    global tournament_rules
    
    # Sanitize content (basic cleanup)
    if content:
        content = content.strip()
    
    # Update rules with metadata
    tournament_rules['rules'] = {
        'content': content,
        'last_updated': datetime.datetime.utcnow().isoformat(),
        'updated_by': {
            'user_id': user_id,
            'username': username
        },
        'version': tournament_rules.get('rules', {}).get('version', 0) + 1
    }
    
    return save_rules()

