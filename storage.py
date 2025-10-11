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
ORG_ROLE_CONFIG_FILE = 'org_role_config.json'

# Global storage
scheduled_events = {}
tournament_rules = {}
org_role_config = {}

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

# ===========================================================================================
# ORG ROLE CONFIGURATION MANAGEMENT
# ===========================================================================================

def load_org_role_config() -> dict:
    """Load organization role configuration from file"""
    global org_role_config
    try:
        if os.path.exists(ORG_ROLE_CONFIG_FILE):
            with open(ORG_ROLE_CONFIG_FILE, 'r', encoding='utf-8') as f:
                org_role_config = json.load(f)
                print(f"Loaded org role configuration from file")
                return org_role_config
    except Exception as e:
        print(f"Error loading org role config: {e}")
    org_role_config = {}
    return org_role_config

def save_org_role_config() -> bool:
    """Save organization role configuration to file"""
    try:
        with open(ORG_ROLE_CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(org_role_config, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error saving org role config: {e}")
        return False

def get_org_role_config(guild_id: str) -> dict:
    """Get org role config for a specific guild"""
    return org_role_config.get(guild_id, {})

def set_org_role_channel(guild_id: str, channel_id: int, user_id: int) -> bool:
    """Set the channel for org role participant posts"""
    global org_role_config
    
    if guild_id not in org_role_config:
        org_role_config[guild_id] = {}
    
    org_role_config[guild_id]['channel_id'] = channel_id
    org_role_config[guild_id]['last_updated'] = datetime.datetime.utcnow().isoformat()
    org_role_config[guild_id]['updated_by'] = user_id
    
    return save_org_role_config()

def set_org_role_spreadsheet(guild_id: str, spreadsheet_url: str, team_name_col: str, 
                             captain_id_col: str, user_id: int) -> bool:
    """Set the spreadsheet configuration for org role"""
    global org_role_config
    
    if guild_id not in org_role_config:
        org_role_config[guild_id] = {}
    
    org_role_config[guild_id]['spreadsheet'] = {
        'url': spreadsheet_url,
        'team_name_column': team_name_col,
        'captain_id_column': captain_id_col
    }
    org_role_config[guild_id]['last_updated'] = datetime.datetime.utcnow().isoformat()
    org_role_config[guild_id]['updated_by'] = user_id
    
    return save_org_role_config()

def add_org_role_posted_message(guild_id: str, message_id: int, channel_id: int, 
                                 team_data: dict) -> bool:
    """Track a posted participant message for later updates"""
    global org_role_config
    
    if guild_id not in org_role_config:
        org_role_config[guild_id] = {}
    
    if 'posted_messages' not in org_role_config[guild_id]:
        org_role_config[guild_id]['posted_messages'] = []
    
    org_role_config[guild_id]['posted_messages'].append({
        'message_id': message_id,
        'channel_id': channel_id,
        'team_data': team_data,
        'posted_at': datetime.datetime.utcnow().isoformat()
    })
    
    return save_org_role_config()

def get_org_role_posted_messages(guild_id: str) -> list:
    """Get all posted participant messages for a guild"""
    config = org_role_config.get(guild_id, {})
    return config.get('posted_messages', [])

def update_org_role_posted_message(guild_id: str, message_id: int, new_team_data: dict) -> bool:
    """Update team data for a posted message"""
    global org_role_config
    
    if guild_id not in org_role_config:
        return False
    
    messages = org_role_config[guild_id].get('posted_messages', [])
    for msg in messages:
        if msg['message_id'] == message_id:
            msg['team_data'] = new_team_data
            msg['updated_at'] = datetime.datetime.utcnow().isoformat()
            return save_org_role_config()
    
    return False

