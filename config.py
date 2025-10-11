"""
Configuration constants for the ASM Tournament Bot
"""

# Channel IDs for event management
CHANNEL_IDS = {
    "take_schedule": 1281967638360359067,    # Schedule channel for posting match schedules
    "results": 1281967703506026538,          # Results channel for posting match outcomes
    "staff_attendance": 1378979992641339403  # Attendance channel for staff tracking
}

# Bot owner ID - has access to all commands
BOT_OWNER_ID = 1251442077561131059

# Role IDs for permissions
ROLE_IDS = {
    "judge": 1261723119257915412,        # Judge role
    "bot_op": 1242280627991220275,       # Bot operator role
    "organizer": 1314905337437880340,    # Organizer role
    "bot_admin": [1242280443898761236, 981116079269109760]     # Bot admin role (full server permissions)
}

# Branding constants
ORGANIZATION_NAME = "ASM Tournament Bot"
TOURNAMENT_SYSTEM_NAME = "ASM Tournament Bot"

