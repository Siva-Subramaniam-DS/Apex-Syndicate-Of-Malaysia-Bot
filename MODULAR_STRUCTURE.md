# ASM Tournament Bot - Modular Structure

## Overview

The bot code has been refactored into a modular architecture for better maintainability, readability, and organization.

## Module Structure

### 1. **config.py**
Contains all configuration constants and IDs:
- `CHANNEL_IDS` - Channel IDs for event management
- `BOT_OWNER_ID` - Bot owner ID
- `ROLE_IDS` - Role IDs for permissions (judge, bot_op, organizer, bot_admin)
- `ORGANIZATION_NAME` - Branding constant
- `TOURNAMENT_SYSTEM_NAME` - Tournament system name

### 2. **storage.py**
Handles all data persistence operations:
- `scheduled_events` - Global storage for scheduled events
- `tournament_rules` - Global storage for tournament rules
- `load_scheduled_events()` - Load events from JSON file
- `save_scheduled_events()` - Save events to JSON file
- `load_tour_panel_config()` - Load tour panel configuration
- `save_tour_panel_config()` - Save tour panel configuration
- `load_rules()` - Load tournament rules
- `save_rules()` - Save tournament rules
- `get_current_rules()` - Get current rules content
- `set_rules_content()` - Set new rules with metadata

### 3. **utils.py**
Utility functions for permissions, embed manipulation, and calculations:

#### Permission Checks:
- `has_organizer_permission(interaction)` - Check organizer permissions
- `has_event_create_permission(interaction)` - Check event creation permissions
- `has_event_result_permission(interaction)` - Check result posting permissions

#### Embed Manipulation:
- `find_field_index(embed, field_name)` - Find field index in embed
- `remove_field_by_name(embed, field_name)` - Remove field from embed
- `update_judge_field(embed, judge_member)` - Update/add judge field
- `remove_judge_field(embed)` - Remove judge field
- `add_green_circle_to_title(title)` - Add green circle emoji
- `update_embed_title_with_green_circle(embed)` - Update title with 🟢
- `replace_green_circle_with_checkmark(title)` - Replace 🟢 with ✅
- `update_embed_title_with_checkmark(embed)` - Update title with checkmark

#### Channel & Permissions:
- `check_bot_permissions(channel)` - Check bot permissions

#### Judge Assignment Tracking:
- `can_judge_take_schedule(judge_id, max_assignments)` - Check if judge can take schedule
- `add_judge_assignment(judge_id, event_id)` - Add schedule to judge
- `remove_judge_assignment(judge_id, event_id)` - Remove schedule from judge

#### Time Calculations:
- `calculate_time_difference(event_datetime, user_timezone)` - Calculate time diff with timezone support

#### Global Storage:
- `reminder_tasks` - Per-event reminder tasks
- `cleanup_tasks` - Per-event cleanup tasks
- `judge_assignments` - Judge assignment tracking

### 4. **graphics.py**
Handles poster/image generation for events:
- `download_google_font(font_family, font_style, font_weight)` - Download Google Fonts
- `get_font_with_fallbacks(font_name, size, font_style)` - Get font with fallbacks
- `sanitize_username_for_poster(username)` - Convert usernames to poster-friendly ASCII
- `get_random_template()` - Get random template from Templates folder
- `create_event_poster(...)` - Create event poster with text overlays

### 5. **sheets.py**
Google Sheets integration for team data:
- `extract_sheet_id_from_url(url)` - Extract Google Sheets ID from URL
- `fetch_sheet_data(sheet_url, team_name_col, captain_id_col)` - Fetch team data from sheet

### 6. **reminders.py**
Event reminders and scheduling system:
- `send_ten_minute_reminder(...)` - Send 10-minute match reminder
- `schedule_ten_minute_reminder(...)` - Schedule 10-minute reminder
- `schedule_event_reminder_v2(...)` - Schedule event reminder using stored datetime
- `schedule_event_cleanup(event_id, delay_hours, bot)` - Schedule event cleanup after delay

### 7. **views.py**
Discord UI Views and Modals:

#### Views:
- `TournamentPanelView` - Interactive tournament panel with registration buttons
  - View Teams button
  - Refresh Data button  
  - Tournament Info button

- `TakeScheduleButton` - View for judges to take schedules
  - Take Schedule button with permission checks
  - Judge assignment notification
  - Embed updates

- `RulesManagementView` - Rule management interface for organizers
  - Enter Rules button
  - Reedit Rules button
  - Show Rules button

#### Modals:
- `RuleInputModal` - Modal for entering/editing tournament rules

#### Functions:
- `display_rules(interaction, tournament_rules)` - Display current rules in embed

### 8. **main.py**
Contains:
- Bot initialization and configuration
- Event handlers (`on_ready`, `on_message`)
- All slash commands:
  - `/rules` - Manage/view tournament rules
  - `/team_balance` - Balance teams by player levels
  - `/add_captain` - Add captains and rename channel
  - `/event-create` - Create tournament event
  - `/event-result` - Add event results
  - `/event-delete` - Delete scheduled event
  - `/event-edit` - Edit event in channel
  - `/exchange_judge` - Exchange judges for events
  - `/time` - Get random match time
  - `/maps` - Randomly select maps
  - `/setup_tour_panel` - Setup tournament panel
  - `/choose` - Randomly choose from options
  - `/unassigned_events` - List events without judges
  - `/general_tie_breaker` - Tie breaker system

## Usage

### Importing Modules

```python
# In main.py or other files
from config import CHANNEL_IDS, BOT_OWNER_ID, ROLE_IDS
from storage import scheduled_events, load_scheduled_events, save_scheduled_events
from utils import has_organizer_permission, update_embed_title_with_checkmark
from graphics import create_event_poster, get_random_template
from sheets import fetch_sheet_data
from reminders import schedule_ten_minute_reminder
from views import TournamentPanelView, TakeScheduleButton, RulesManagementView
```

### Benefits of Modular Structure

1. **Better Organization** - Related functionality grouped together
2. **Easier Maintenance** - Changes to specific features isolated to their modules
3. **Improved Readability** - Smaller, focused files instead of one massive file
4. **Reusability** - Modules can be imported and used in different contexts
5. **Easier Testing** - Individual modules can be tested independently
6. **Reduced Coupling** - Clear separation of concerns
7. **Better Collaboration** - Multiple developers can work on different modules

### File Structure

```
Apex Malaysia/
├── main.py                    # Bot initialization, event handlers, commands
├── config.py                  # Configuration constants
├── storage.py                 # Data persistence
├── utils.py                   # Utility functions
├── graphics.py                # Poster/image generation
├── sheets.py                  # Google Sheets integration
├── reminders.py               # Event reminders & scheduling
├── views.py                   # Discord UI components
├── commands/                  # Command modules (future expansion)
│   └── __init__.py
├── Fonts/                     # Font files for posters
├── Templates/                 # Template images for posters
├── scheduled_events.json      # Persistent event data
├── tournament_rules.json      # Persistent rules data
├── tour_panel_config.json     # Tournament panel config
└── .env                       # Environment variables
```

## Next Steps

### Cleanup Recommendations

1. **Remove Duplicate Code in main.py**
   - The functions now in modules still exist in main.py
   - Gradually remove duplicates as you verify imports work correctly
   - Test after each removal to ensure nothing breaks

2. **Further Modularization**
   - Consider moving commands to separate files in `commands/` folder
   - Group related commands (event commands, tournament commands, utility commands)

3. **Add Type Hints**
   - Add comprehensive type hints to all module functions
   - Improves IDE autocomplete and catches errors early

4. **Documentation**
   - Add docstrings to all functions
   - Create inline code comments for complex logic

5. **Error Handling**
   - Centralize error handling in a dedicated module
   - Create custom exception classes

6. **Testing**
   - Create unit tests for utility functions
   - Integration tests for command flows

## Migration Notes

⚠️ **Important**: The current main.py still contains duplicate code. The imports have been added at the top, but the original function definitions remain in the file. This ensures backwards compatibility while transitioning.

To complete the migration:
1. Verify all imports work correctly
2. Run the bot and test key functionality
3. Gradually remove duplicate functions from main.py
4. Test after each removal

## Support

For questions or issues with the modular structure, refer to individual module documentation or contact the development team.

