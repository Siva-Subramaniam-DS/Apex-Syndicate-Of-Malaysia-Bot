# Org Role Commands - Quick Reference

## Commands Summary

| Command | Description | Required Setup |
|---------|-------------|----------------|
| `/set_channel_org_role` | Set channel for posting participants | None |
| `/set_spreadsheet_org_role` | Configure Google Sheets data source | None |
| `/check_duplicates_org_role` | Check for duplicate teams/captains | Spreadsheet |
| `/post_participants_org_role` | Post participant list to channel | Channel + Spreadsheet |
| `/update_team_info_org_role` | Update team info in posted messages | Spreadsheet |

## Quick Start (3 Steps)

### 1️⃣ Set Your Channel
```
/set_channel_org_role channel:#participants
```

### 2️⃣ Configure Your Spreadsheet
```
/set_spreadsheet_org_role 
  spreadsheet_url: https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID/edit
  team_name_column: Team Name
  captain_id_column: Captain ID
```

### 3️⃣ Post Participants
```
/post_participants_org_role title: My Tournament Participants
```

## Common Use Cases

### Check for Duplicates Before Posting
```
1. /check_duplicates_org_role
2. [Fix duplicates in spreadsheet if any]
3. /post_participants_org_role
```

### Update Team Name
```
/update_team_info_org_role 
  identifier: Old Team Name
  new_team_name: New Team Name
```

### Change Captain
```
/update_team_info_org_role 
  identifier: Team Name
  new_captain_id: 123456789012345678
```

### Update Both Name and Captain
```
/update_team_info_org_role 
  identifier: Team Phoenix
  new_team_name: Phoenix Warriors
  new_captain_id: 987654321098765432
```

## Important Notes

✅ **All commands require Organizer role**  
✅ **Spreadsheet must be publicly accessible**  
✅ **Updates apply to ALL posted participant messages automatically**  
✅ **Captain IDs are Discord user IDs (18-19 digit numbers)**  

❌ **Spreadsheet updates do NOT sync automatically** - Use `/post_participants_org_role` to post updated list  
❌ **Team updates do NOT modify the spreadsheet** - Only Discord messages are updated  

## Getting Discord User IDs

1. Enable Developer Mode: Settings → Advanced → Developer Mode
2. Right-click user → Copy ID
3. Paste into spreadsheet

## Spreadsheet Format

Minimum required structure:
```
| Team Name    | Captain ID          |
|--------------|---------------------|
| Team Alpha   | 123456789012345678  |
| Team Beta    | 234567890123456789  |
```

**Note:** Column names are case-insensitive but must match exactly what you specify in the command.

---

For detailed documentation, see `ORG_ROLE_MANAGEMENT.md`

