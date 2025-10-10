"""
Google Sheets integration module for the ASM Tournament Bot
Handles fetching and processing team data from Google Sheets
"""

import re
import requests
from urllib.parse import urlparse, parse_qs


def extract_sheet_id_from_url(url: str) -> str:
    """Extract Google Sheets ID from various URL formats"""
    try:
        # Handle different Google Sheets URL formats
        if '/spreadsheets/d/' in url:
            match = re.search(r'/spreadsheets/d/([a-zA-Z0-9-_]+)', url)
            if match:
                return match.group(1)
        elif 'docs.google.com/spreadsheets' in url:
            parsed = urlparse(url)
            query = parse_qs(parsed.query)
            if 'id' in query:
                return query['id'][0]
        
        # If it's already just an ID
        if re.match(r'^[a-zA-Z0-9-_]+$', url):
            return url
            
        return None
    except Exception as e:
        print(f"Error extracting sheet ID: {e}")
        return None


async def fetch_sheet_data(sheet_url: str, team_name_col: str, captain_id_col: str) -> list:
    """Fetch data from Google Sheets using public access (no auth required)"""
    try:
        sheet_id = extract_sheet_id_from_url(sheet_url)
        if not sheet_id:
            return []
        
        # Use Google Sheets API v4 public endpoint (read-only)
        api_url = f"https://sheets.googleapis.com/v4/spreadsheets/{sheet_id}/values/Sheet1"
        
        response = requests.get(api_url, timeout=10)
        if response.status_code != 200:
            print(f"Failed to fetch sheet data: {response.status_code}")
            return []
        
        data = response.json()
        values = data.get('values', [])
        
        if not values:
            return []
        
        # Find column indices
        headers = values[0] if values else []
        team_name_idx = None
        captain_id_idx = None
        
        for i, header in enumerate(headers):
            if header.lower() == team_name_col.lower():
                team_name_idx = i
            elif header.lower() == captain_id_col.lower():
                captain_id_idx = i
        
        if team_name_idx is None or captain_id_idx is None:
            print(f"Could not find columns: {team_name_col}, {captain_id_col}")
            return []
        
        # Extract team data
        teams = []
        for row in values[1:]:  # Skip header row
            if len(row) > max(team_name_idx, captain_id_idx):
                team_name = row[team_name_idx].strip()
                captain_id = row[captain_id_idx].strip()
                if team_name and captain_id:
                    teams.append({
                        'name': team_name,
                        'captain_id': captain_id
                    })
        
        return teams
        
    except Exception as e:
        print(f"Error fetching sheet data: {e}")
        return []

