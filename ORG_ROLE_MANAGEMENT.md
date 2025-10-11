# Organization Role Management System

## Overview
The Org Role Management system allows tournament organizers to manage participant lists from Google Sheets and post them to Discord channels. This system includes duplicate detection, team information updates, and automated participant list management.

## Features

### 1. **Set Channel** (`/set_channel_org_role`)
Set the Discord channel where participant lists will be posted.

**Usage:**
```
/set_channel_org_role channel:#participants
```

**Parameters:**
- `channel`: The Discord channel where participant lists will be posted

**Permissions:** Organizer role required

**Example:**
- Command: `/set_channel_org_role channel:#tournament-participants`
- Result: All future participant lists will be posted to #tournament-participants

---

### 2. **Set Spreadsheet** (`/set_spreadsheet_org_role`)
Configure the Google Sheets spreadsheet that contains participant data.

**Usage:**
```
/set_spreadsheet_org_role 
  spreadsheet_url: <Google Sheets URL or ID>
  team_name_column: <Column name for team names>
  captain_id_column: <Column name for captain Discord IDs>
```

**Parameters:**
- `spreadsheet_url`: Google Sheets URL or ID (must be publicly accessible)
- `team_name_column`: The exact column name containing team names (e.g., "Team Name")
- `captain_id_column`: The exact column name containing captain Discord IDs (e.g., "Captain ID")

**Permissions:** Organizer role required

**Requirements:**
- The spreadsheet must be publicly accessible (Anyone with the link can view)
- Column names must match exactly (case-insensitive)
- Captain IDs should be Discord user IDs (numbers)

**Example:**
```
/set_spreadsheet_org_role 
  spreadsheet_url: https://docs.google.com/spreadsheets/d/1ABC...XYZ/edit
  team_name_column: Team Name
  captain_id_column: Captain ID
```

**Success Response:**
- Shows number of teams found
- Displays first 5 teams as preview
- Validates that columns exist and data can be fetched

---

### 3. **Check Duplicates** (`/check_duplicates_org_role`)
Check for duplicate team names or captain IDs in the configured spreadsheet.

**Usage:**
```
/check_duplicates_org_role
```

**Parameters:** None

**Permissions:** Organizer role required

**What it checks:**
- Duplicate team names (teams with the same name)
- Duplicate captain IDs (same person registered multiple times)

**Response:**
- ✅ **No Duplicates Found:** All entries are unique
- ⚠️ **Duplicates Found:** Lists all duplicate team names and captain IDs
  - Shows first 10 duplicates of each type
  - Displays total counts of unique names and captains

**Example Output:**
```
⚠️ Duplicates Found

Duplicate Team Names (2)
• Team Phoenix (2 times)
• Elite Squad (2 times)

Duplicate Captain IDs (1)
• 123456789012345678 (2 teams)

Total Teams: 50
Unique Names: 48
Unique Captains: 49
```

---

### 4. **Post Participants** (`/post_participants_org_role`)
Post the participant list from the spreadsheet to the configured channel.

**Usage:**
```
/post_participants_org_role title: <Optional title>
```

**Parameters:**
- `title` (optional): Custom title for the participant list (default: "Tournament Participants")

**Permissions:** Organizer role required

**Prerequisites:**
- Channel must be set using `/set_channel_org_role`
- Spreadsheet must be configured using `/set_spreadsheet_org_role`

**What it does:**
1. Fetches latest data from the configured spreadsheet
2. Creates a formatted embed with all participants
3. Posts to the configured channel
4. Tracks the message for future updates
5. Mentions each captain using Discord mentions

**Embed Format:**
- Title: 📋 [Your Custom Title]
- Description: Total participant count
- Fields: Teams listed with numbers, team names, and captain mentions
- Footer: Organization name and poster's username
- Timestamp: When the list was posted

**Example:**
```
/post_participants_org_role title: KOTS Season 5 Participants
```

**Features:**
- Automatically splits into multiple fields if more than 20 teams
- Shows jump link to the posted message in confirmation
- Captain IDs are converted to Discord mentions (@username)

---

### 5. **Update Team Info** (`/update_team_info_org_role`)
Update team information in previously posted participant messages.

**Usage:**
```
/update_team_info_org_role 
  identifier: <Team name or Captain ID>
  new_team_name: <New team name (optional)>
  new_captain_id: <New captain ID (optional)>
```

**Parameters:**
- `identifier`: Team name or Captain Discord ID to find the team
- `new_team_name` (optional): New name for the team
- `new_captain_id` (optional): New captain Discord ID

**Permissions:** Organizer role required

**What it does:**
1. Searches for the team by name or captain ID
2. Updates the team information
3. Automatically refreshes ALL previously posted participant messages
4. Updates timestamps and attribution

**Important Notes:**
- At least one field (team name or captain ID) must be provided
- Updates are applied to ALL posted participant messages automatically
- Original spreadsheet is NOT modified (this only updates Discord messages)
- Identifier search is case-insensitive for team names

**Example 1 - Update team name:**
```
/update_team_info_org_role 
  identifier: Team Phoenix
  new_team_name: Phoenix Rising
```

**Example 2 - Update captain:**
```
/update_team_info_org_role 
  identifier: 123456789012345678
  new_captain_id: 987654321098765432
```

**Example 3 - Update both:**
```
/update_team_info_org_role 
  identifier: Elite Squad
  new_team_name: Elite Warriors
  new_captain_id: 111222333444555666
```

**Success Response:**
- Shows what changed (old → new values)
- Reports how many messages were updated
- Shows who made the update

---

## Workflow Example

### Initial Setup
1. Set the channel for participant lists:
   ```
   /set_channel_org_role channel:#participants
   ```

2. Configure the Google Spreadsheet:
   ```
   /set_spreadsheet_org_role 
     spreadsheet_url: https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID/edit
     team_name_column: Team Name
     captain_id_column: Captain ID
   ```

3. Check for duplicates (recommended before posting):
   ```
   /check_duplicates_org_role
   ```

4. Post participants to channel:
   ```
   /post_participants_org_role title: Tournament Season 5 Participants
   ```

### During Tournament
- If a team changes their name:
  ```
  /update_team_info_org_role 
    identifier: Old Team Name
    new_team_name: New Team Name
  ```

- If a captain changes:
  ```
  /update_team_info_org_role 
    identifier: Team Name
    new_captain_id: 123456789012345678
  ```

- Recheck for duplicates if new teams are added to the spreadsheet:
  ```
  /check_duplicates_org_role
  ```

- Post updated participant list (if spreadsheet changed):
  ```
  /post_participants_org_role title: Updated Participant List
  ```

---

## Google Sheets Setup Guide

### Step 1: Prepare Your Spreadsheet
1. Create or open your Google Spreadsheet
2. Ensure the first row contains column headers
3. Required columns:
   - **Team Name** (or your chosen name)
   - **Captain ID** (or your chosen name)

### Step 2: Get Captain Discord IDs
To get a user's Discord ID:
1. Enable Developer Mode in Discord (User Settings → Advanced → Developer Mode)
2. Right-click on the user → Copy ID
3. Paste the ID into the spreadsheet

### Step 3: Make Spreadsheet Public
1. Click "Share" button in Google Sheets
2. Click "Change to anyone with the link"
3. Set permission to "Viewer"
4. Copy the link

### Example Spreadsheet Structure:
```
| Team Name       | Captain ID          | Player 2 | Player 3 |
|-----------------|---------------------|----------|----------|
| Team Phoenix    | 123456789012345678  | Alice    | Bob      |
| Elite Squad     | 234567890123456789  | Charlie  | Dave     |
| Dragon Force    | 345678901234567890  | Eve      | Frank    |
```

**Note:** Only "Team Name" and "Captain ID" columns are required for the bot. You can have additional columns for other information.

---

## Permissions

All org role commands require the **Organizer** role as defined in `config.py`:
- Role ID is configured in `ROLE_IDS["organizer"]`
- Bot owner (defined in `BOT_OWNER_ID`) has access to all commands

---

## Troubleshooting

### "Could not fetch data from spreadsheet"
- Ensure the spreadsheet is publicly accessible (Anyone with the link can view)
- Check that column names match exactly (case-insensitive)
- Verify the spreadsheet URL is correct
- Make sure Sheet1 (first sheet) contains your data

### "No spreadsheet configured"
- Run `/set_spreadsheet_org_role` first before using other commands

### "No channel configured"
- Run `/set_channel_org_role` first before posting participants

### "Team not found"
- Check spelling of team name (case-insensitive)
- Try using the captain's Discord ID instead
- Verify the team exists in the spreadsheet

### Messages not updating
- Check that the bot has permissions to edit messages in the channel
- Verify messages weren't deleted
- Ensure the bot is still in the server

---

## Data Persistence

All configuration is stored in `org_role_config.json`:
- Channel settings
- Spreadsheet configuration
- Posted message tracking
- Update history

This file is automatically created and updated by the bot. **Do not manually edit this file** unless you know what you're doing.

---

## Technical Notes

### Message Tracking
- The bot tracks all posted participant messages
- When you update team info, ALL previously posted messages are updated
- This allows you to maintain multiple participant lists (e.g., different channels) that stay in sync

### Rate Limiting
- Google Sheets API has rate limits
- The bot caches data where possible
- If you encounter rate limiting, wait a few minutes before retrying

### Embed Limits
- Discord embeds have a limit of 25 fields
- Each field can have max 1024 characters
- The bot automatically splits large participant lists into multiple fields
- Maximum teams per field: 20

---

## Support

For issues or feature requests, contact the bot administrator or check the main bot documentation in `MODULAR_STRUCTURE.md`.

---

**Version:** 1.0  
**Last Updated:** 2025-10-11  
**Compatible With:** ASM Tournament Bot v3.0+

