"""
Utility functions for the ASM Tournament Bot
Includes permissions checks, embed manipulation, and time calculations
"""

import discord
import datetime
import pytz
from config import BOT_OWNER_ID, ROLE_IDS

# Track per-event reminder tasks (for cancellation/update)
reminder_tasks = {}

# Track per-event cleanup tasks (to remove finished events after result)
cleanup_tasks = {}

# Store judge assignments to prevent overloading
judge_assignments = {}  # {judge_id: [event_ids]}


# ===========================================================================================
# PERMISSION CHECKS
# ===========================================================================================

def has_organizer_permission(interaction):
    """Check if user has organizer permissions for rule management (Bot Owner or Organizer)"""
    # Bot Owner bypass
    if interaction.user.id == BOT_OWNER_ID:
        return True
    
    organizer_role = discord.utils.get(interaction.user.roles, id=ROLE_IDS["organizer"])
    return organizer_role is not None

def has_event_create_permission(interaction):
    """Check if user has permission to create events (Bot Owner, Organizer or Bot Op)"""
    # Bot Owner bypass
    if interaction.user.id == BOT_OWNER_ID:
        return True
    
    organizer_role = discord.utils.get(interaction.user.roles, id=ROLE_IDS["organizer"])
    bot_op_role = discord.utils.get(interaction.user.roles, id=ROLE_IDS["bot_op"])
    return organizer_role is not None or bot_op_role is not None

def has_event_result_permission(interaction):
    """Check if user has permission to post event results (Bot Owner, Organizer or Judge)"""
    # Bot Owner bypass
    if interaction.user.id == BOT_OWNER_ID:
        return True
    
    organizer_role = discord.utils.get(interaction.user.roles, id=ROLE_IDS["organizer"])
    judge_role = discord.utils.get(interaction.user.roles, id=ROLE_IDS["judge"])
    return organizer_role is not None or judge_role is not None


# ===========================================================================================
# EMBED MANIPULATION
# ===========================================================================================

def find_field_index(embed: discord.Embed, field_name: str) -> int:
    """Find the index of a field by name. Returns -1 if not found."""
    try:
        for i, field in enumerate(embed.fields):
            if field.name == field_name:
                return i
        return -1
    except Exception as e:
        print(f"Error finding field index: {e}")
        return -1

def remove_field_by_name(embed: discord.Embed, field_name: str) -> bool:
    """Safely remove a field by name using Discord.py methods. Returns True if removed, False if not found."""
    try:
        field_index = find_field_index(embed, field_name)
        if field_index != -1:
            embed.remove_field(field_index)
            return True
        return False
    except Exception as e:
        print(f"Error removing field by name '{field_name}': {e}")
        return False

def update_judge_field(embed: discord.Embed, judge_member: discord.Member) -> bool:
    """Update or add judge field safely. Returns True if successful."""
    try:
        # Remove existing judge field if it exists
        remove_field_by_name(embed, "👨‍⚖️ Judge")
        
        # Add new judge field
        embed.add_field(
            name="👨‍⚖️ Judge", 
            value=f"{judge_member.mention} `@{judge_member.name}`", 
            inline=True
        )
        return True
    except Exception as e:
        print(f"Error updating judge field: {e}")
        return False

def remove_judge_field(embed: discord.Embed) -> bool:
    """Remove judge field safely. Returns True if removed, False if not found."""
    try:
        return remove_field_by_name(embed, "👨‍⚖️ Judge")
    except Exception as e:
        print(f"Error removing judge field: {e}")
        return False

def add_green_circle_to_title(title: str) -> str:
    """Add green circle emoji to the beginning of title if not already present"""
    green_circle = "🟢"
    
    # Check if already has green circle
    if title and title.startswith(green_circle):
        return title
    
    # Add green circle to beginning
    return green_circle + (title or "")

def update_embed_title_with_green_circle(embed: discord.Embed) -> bool:
    """Update embed title with green circle, returns success status"""
    try:
        if embed.title:
            new_title = add_green_circle_to_title(embed.title)
            embed.title = new_title
            return True
        return False
    except Exception as e:
        print(f"Error updating embed title with green circle: {e}")
        return False

def replace_green_circle_with_checkmark(title: str) -> str:
    """Replace green circle emoji with checkmark emoji in title"""
    green_circle = "🟢"
    checkmark = "✅"
    
    if title and title.startswith(green_circle):
        return checkmark + title[len(green_circle):]
    
    # If no green circle, just add checkmark at the beginning
    return checkmark + (title or "")

def update_embed_title_with_checkmark(embed: discord.Embed) -> bool:
    """Update embed title with checkmark, returns success status"""
    try:
        if embed.title:
            new_title = replace_green_circle_with_checkmark(embed.title)
            embed.title = new_title
            return True
        return False
    except Exception as e:
        print(f"Error updating embed title with checkmark: {e}")
        return False


# ===========================================================================================
# CHANNEL & PERMISSIONS
# ===========================================================================================

def check_bot_permissions(channel: discord.TextChannel) -> dict:
    """Check if bot has necessary permissions in a channel"""
    if not channel:
        return {"can_edit": False, "reason": "Channel not found"}
    
    bot_member = channel.guild.me
    if not bot_member:
        return {"can_edit": False, "reason": "Bot not found in guild"}
    
    permissions = channel.permissions_for(bot_member)
    
    required_perms = {
        "read_messages": permissions.read_messages,
        "send_messages": permissions.send_messages,
        "embed_links": permissions.embed_links,
        "read_message_history": permissions.read_message_history
    }
    
    missing_perms = [perm for perm, has_perm in required_perms.items() if not has_perm]
    
    if missing_perms:
        return {"can_edit": False, "reason": f"Missing permissions: {', '.join(missing_perms)}"}
    
    return {"can_edit": True, "reason": "All permissions available"}


# ===========================================================================================
# JUDGE ASSIGNMENT TRACKING
# ===========================================================================================

def can_judge_take_schedule(judge_id: int, max_assignments: int = 3) -> tuple[bool, str]:
    """Check if a judge can take another schedule"""
    if judge_id not in judge_assignments:
        return True, ""
    
    current_assignments = len(judge_assignments[judge_id])
    if current_assignments >= max_assignments:
        return False, f"You already have {current_assignments} schedule(s) assigned. Maximum allowed is {max_assignments}."
    
    return True, ""

def add_judge_assignment(judge_id: int, event_id: str):
    """Add a schedule assignment to a judge"""
    if judge_id not in judge_assignments:
        judge_assignments[judge_id] = []
    judge_assignments[judge_id].append(event_id)

def remove_judge_assignment(judge_id: int, event_id: str):
    """Remove a schedule assignment from a judge"""
    if judge_id in judge_assignments and event_id in judge_assignments[judge_id]:
        judge_assignments[judge_id].remove(event_id)
        if not judge_assignments[judge_id]:  # Remove empty list
            del judge_assignments[judge_id]


# ===========================================================================================
# TIME CALCULATIONS
# ===========================================================================================

def calculate_time_difference(event_datetime: datetime.datetime, user_timezone: str = None) -> dict:
    """Calculate time difference and format for different timezones"""
    current_time = datetime.datetime.now()
    time_diff = event_datetime - current_time
    minutes_remaining = int(time_diff.total_seconds() / 60)
    
    # Format UTC time exactly as requested
    utc_time_str = event_datetime.strftime("%H:%M utc, %d/%m")
    
    # Try to detect user's local timezone
    local_timezone = None
    if user_timezone:
        try:
            local_timezone = pytz.timezone(user_timezone)
        except:
            pass
    
    # If no user timezone provided, try to detect from system
    if not local_timezone:
        try:
            # Try to get system timezone
            import time
            local_timezone = pytz.timezone(time.tzname[time.daylight])
        except:
            # Fallback to IST if detection fails
            local_timezone = pytz.timezone('Asia/Kolkata')
    
    # Calculate user's local time
    local_time = event_datetime.replace(tzinfo=pytz.UTC).astimezone(local_timezone)
    local_time_formatted = local_time.strftime("%A, %d %B, %Y %H:%M")
    
    # Calculate other common timezones
    ist_tz = pytz.timezone('Asia/Kolkata')
    ist_time = event_datetime.replace(tzinfo=pytz.UTC).astimezone(ist_tz)
    ist_formatted = ist_time.strftime("%A, %d %B, %Y %H:%M")
    
    est_tz = pytz.timezone('America/New_York')
    est_time = event_datetime.replace(tzinfo=pytz.UTC).astimezone(est_tz)
    est_formatted = est_time.strftime("%A, %d %B, %Y %H:%M")
    
    gmt_tz = pytz.timezone('Europe/London')
    gmt_time = event_datetime.replace(tzinfo=pytz.UTC).astimezone(gmt_tz)
    gmt_formatted = gmt_time.strftime("%A, %d %B, %Y %H:%M")
    
    return {
        'minutes_remaining': minutes_remaining,
        'utc_time': utc_time_str,
        'utc_time_simple': event_datetime.strftime("%H:%M UTC"),
        'local_time': local_time_formatted,
        'ist_time': ist_formatted,
        'est_time': est_formatted,
        'gmt_time': gmt_formatted
    }

