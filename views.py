"""
Discord UI Views and Modals for the ASM Tournament Bot
Includes TournamentPanelView, TakeScheduleButton, RuleInputModal, and RulesManagementView
"""

import discord
from discord.ui import Button, View
from discord import app_commands
from config import BOT_OWNER_ID, ROLE_IDS, ORGANIZATION_NAME, TOURNAMENT_SYSTEM_NAME
from storage import scheduled_events, get_current_rules, set_rules_content
from utils import (
    can_judge_take_schedule, 
    add_judge_assignment, 
    update_embed_title_with_green_circle,
    update_judge_field
)
from sheets import fetch_sheet_data


class TournamentPanelView(discord.ui.View):
    """Interactive view for tournament panel with registration buttons"""
    
    def __init__(self, tour_name: str, teams_data: list, config: dict):
        super().__init__(timeout=None)  # Persistent view
        self.tour_name = tour_name
        self.teams_data = teams_data
        self.config = config
    
    @discord.ui.button(label="📋 View Teams", style=discord.ButtonStyle.primary, emoji="👥")
    async def view_teams(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Show list of registered teams"""
        if not self.teams_data:
            await interaction.response.send_message("No teams registered yet.", ephemeral=True)
            return
        
        embed = discord.Embed(
            title=f"📋 Registered Teams - {self.tour_name}",
            description=f"**Total Teams:** {len(self.teams_data)}",
            color=discord.Color.blue(),
            timestamp=discord.utils.utcnow()
        )
        
        # Split teams into chunks to avoid embed limits
        teams_text = ""
        for i, team in enumerate(self.teams_data[:20], 1):  # Limit to 20 teams
            teams_text += f"{i}. **{team['name']}** (Captain: <@{team['captain_id']}>)\n"
        
        if teams_text:
            embed.add_field(name="Registered Teams", value=teams_text, inline=False)
        
        if len(self.teams_data) > 20:
            embed.set_footer(text=f"Showing first 20 of {len(self.teams_data)} teams")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @discord.ui.button(label="🔄 Refresh Data", style=discord.ButtonStyle.secondary, emoji="🔄")
    async def refresh_data(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Refresh team data from Google Sheet"""
        try:
            await interaction.response.defer(ephemeral=True)
            
            # Re-fetch data from sheet
            sheet_url = self.config.get('sheet', '')
            team_name_col = self.config.get('columns', {}).get('team_name', '')
            captain_id_col = self.config.get('columns', {}).get('captain_id', '')
            
            new_teams = await fetch_sheet_data(sheet_url, team_name_col, captain_id_col)
            self.teams_data = new_teams
            
            await interaction.followup.send(f"✅ Refreshed! Found {len(new_teams)} teams.", ephemeral=True)
            
        except Exception as e:
            await interaction.followup.send(f"❌ Error refreshing data: {e}", ephemeral=True)
    
    @discord.ui.button(label="📊 Tournament Info", style=discord.ButtonStyle.success, emoji="ℹ️")
    async def tournament_info(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Show tournament information"""
        embed = discord.Embed(
            title=f"📊 {self.tour_name} - Tournament Info",
            color=discord.Color.green(),
            timestamp=discord.utils.utcnow()
        )
        
        deadline = self.config.get('deadline', 'Not specified')
        embed.add_field(name="📅 Registration Deadline", value=deadline, inline=False)
        
        sheet_url = self.config.get('sheet', '')
        if sheet_url:
            embed.add_field(name="📊 Registration Sheet", value=f"[View Sheet]({sheet_url})", inline=False)
        
        # Get channel mentions
        channels = self.config.get('channels', {})
        rules_channel_id = channels.get('rules')
        if rules_channel_id:
            embed.add_field(name="📋 Rules Channel", value=f"<#{rules_channel_id}>", inline=True)
        
        result_channel_id = channels.get('result')
        if result_channel_id:
            embed.add_field(name="🏆 Results Channel", value=f"<#{result_channel_id}>", inline=True)
        
        embed.add_field(name="👥 Registered Teams", value=f"{len(self.teams_data)}", inline=True)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)


class TakeScheduleButton(View):
    def __init__(self, event_id: str, team1_captain: discord.Member, team2_captain: discord.Member, event_channel: discord.TextChannel = None):
        super().__init__(timeout=None)
        self.event_id = event_id
        self.team1_captain = team1_captain
        self.team2_captain = team2_captain
        self.event_channel = event_channel
        self.judge = None
        self._taking_schedule = False  # Flag to prevent race conditions
        
    @discord.ui.button(label="Take Schedule", style=discord.ButtonStyle.green, emoji="📋")
    async def take_schedule(self, interaction: discord.Interaction, button: Button):
        # Prevent race conditions by checking if someone is already taking the schedule
        if self._taking_schedule:
            await interaction.response.send_message("⏳ Another judge is currently taking this schedule. Please wait a moment.", ephemeral=True)
            return
            
        # Check if user has Judge or Organizer role, or is Bot Owner
        if interaction.user.id != BOT_OWNER_ID:
            organizer_role = discord.utils.get(interaction.user.roles, id=ROLE_IDS["organizer"])
            judge_role = discord.utils.get(interaction.user.roles, id=ROLE_IDS["judge"])
            if not (organizer_role or judge_role):
                await interaction.response.send_message("❌ You need **Organizer** or **Judge** role to take this schedule.", ephemeral=True)
                return
            
        # Check if already taken
        if self.judge:
            await interaction.response.send_message(f"❌ This schedule has already been taken by {self.judge.display_name}.", ephemeral=True)
            return
        
        # Check if judge can take more schedules
        can_take, error_message = can_judge_take_schedule(interaction.user.id, max_assignments=7)
        if not can_take:
            await interaction.response.send_message(f"❌ {error_message}", ephemeral=True)
            return
        
        # Set flag to prevent race conditions
        self._taking_schedule = True
        
        try:
            # Defer response to give us time to process
            await interaction.response.defer(ephemeral=True)
            
            # Double-check if still available (in case another judge took it while we were processing)
            if self.judge:
                await interaction.followup.send(f"❌ This schedule has already been taken by {self.judge.display_name}.", ephemeral=True)
                return
            
            # Assign judge
            self.judge = interaction.user
            
            # Add to judge assignments tracking
            add_judge_assignment(interaction.user.id, self.event_id)
            
            # Update button appearance
            button.label = f"Taken by {interaction.user.display_name}"
            button.style = discord.ButtonStyle.gray
            button.disabled = True
            button.emoji = "✅"
            
            # Update the embed
            embed = interaction.message.embeds[0]
            embed.color = discord.Color.green()
            
            # Update title with green circle
            title_update_success = update_embed_title_with_green_circle(embed)
            if not title_update_success:
                print(f"Warning: Failed to update title for event {self.event_id}")
            
            # Update judge field using safe utility function
            if not update_judge_field(embed, interaction.user):
                await interaction.followup.send("❌ Failed to update embed with judge information.", ephemeral=True)
                return
            
            # Update the message with the updated take button only
            try:
                await interaction.message.edit(embed=embed, view=self)
            except discord.Forbidden:
                await interaction.followup.send("❌ Bot doesn't have permission to edit messages in this channel.", ephemeral=True)
                return
            except Exception as e:
                print(f"Error editing message: {e}")
                await interaction.followup.send("❌ Failed to update message.", ephemeral=True)
                return
            
            # Send success message
            await interaction.followup.send("✅ You have successfully taken this schedule!", ephemeral=True)
            
            # Send notification to the event channel
            await self.send_judge_assignment_notification(interaction.user)
            
            # Update scheduled events with judge
            if self.event_id in scheduled_events:
                scheduled_events[self.event_id]['judge'] = self.judge
            
        except Exception as e:
            # Reset flag in case of error
            self._taking_schedule = False
            print(f"Error in take_schedule: {e}")
            await interaction.followup.send(f"❌ An error occurred while taking the schedule: {str(e)}", ephemeral=True)
        finally:
            # Reset flag after processing
            self._taking_schedule = False

    
    async def send_judge_assignment_notification(self, judge: discord.Member):
        """Send notification to the event channel when a judge is assigned and add judge to channel"""
        if not self.event_channel:
            return
        
        try:
            # Add judge to the event channel with proper permissions
            await self.event_channel.set_permissions(
                judge, 
                read_messages=True, 
                send_messages=True, 
                view_channel=True,
                embed_links=True,
                attach_files=True,
                read_message_history=True
            )
            
            # Create notification embed
            embed = discord.Embed(
                title="👨‍⚖️ Judge Assigned",
                description=f"**{judge.display_name}** has been assigned as the judge for this match!",
                color=discord.Color.green(),
                timestamp=discord.utils.utcnow()
            )
            
            embed.add_field(
                name="📋 Match Details",
                value=f"**Team 1:** {self.team1_captain.mention}\n**Team 2:** {self.team2_captain.mention}",
                inline=False
            )
            
            embed.add_field(
                name="👨‍⚖️ Judge",
                value=f"{judge.mention} `@{judge.name}`\n✅ **Added to channel**",
                inline=True
            )
            
            embed.set_footer(text=f"Powered by • {ORGANIZATION_NAME}")
            
            # Send notification to the event channel
            await self.event_channel.send(
                content=f"🔔 {judge.mention} {self.team1_captain.mention} {self.team2_captain.mention}",
                embed=embed
            )
            
        except discord.Forbidden:
            print(f"Error: Bot doesn't have permission to add {judge.display_name} to channel {self.event_channel.name}")
        except Exception as e:
            print(f"Error sending judge assignment notification: {e}")


# ===========================================================================================
# RULE MANAGEMENT UI COMPONENTS
# ===========================================================================================

class RuleInputModal(discord.ui.Modal):
    """Modal for entering/editing rule content"""
    
    def __init__(self, title: str, current_content: str = ""):
        super().__init__(title=title)
        
        # Text input field for rule content
        self.rule_input = discord.ui.TextInput(
            label="Tournament Rules",
            placeholder="Enter the tournament rules here...",
            default=current_content,
            style=discord.TextStyle.paragraph,
            max_length=4000,
            required=False
        )
        self.add_item(self.rule_input)
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            # Get the content from the input
            content = self.rule_input.value.strip()
            
            # Save the rules
            success = set_rules_content(content, interaction.user.id, interaction.user.name)
            
            if success:
                # Create confirmation embed
                embed = discord.Embed(
                    title="✅ Rules Updated Successfully",
                    description="Tournament rules have been saved.",
                    color=discord.Color.green(),
                    timestamp=discord.utils.utcnow()
                )
                
                if content:
                    # Show preview of rules (truncated if too long)
                    preview = content[:500] + "..." if len(content) > 500 else content
                    embed.add_field(name="Rules Preview", value=f"```\n{preview}\n```", inline=False)
                else:
                    embed.add_field(name="Status", value="Rules have been cleared (empty)", inline=False)
                
                embed.set_footer(text=f"Updated by {interaction.user.name}")
                
                await interaction.response.send_message(embed=embed, ephemeral=True)
            else:
                await interaction.response.send_message("❌ Failed to save rules. Please try again.", ephemeral=True)
                
        except Exception as e:
            print(f"Error in rule modal submission: {e}")
            await interaction.response.send_message("❌ An error occurred while saving rules.", ephemeral=True)


class RulesManagementView(discord.ui.View):
    """Interactive view for organizers with rule management buttons"""
    
    def __init__(self):
        super().__init__(timeout=300)  # 5 minute timeout
    
    @discord.ui.button(label="Enter Rules", style=discord.ButtonStyle.green, emoji="📝")
    async def enter_rules(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Button to enter new rules"""
        modal = RuleInputModal("Enter Tournament Rules")
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="Reedit Rules", style=discord.ButtonStyle.primary, emoji="✏️")
    async def reedit_rules(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Button to edit existing rules"""
        current_rules = get_current_rules()
        
        if not current_rules:
            await interaction.response.send_message("❌ No rules are currently set. Use 'Enter Rules' to create new rules.", ephemeral=True)
            return
        
        modal = RuleInputModal("Edit Tournament Rules", current_rules)
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="Show Rules", style=discord.ButtonStyle.secondary, emoji="👁️")
    async def show_rules(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Button to display current rules"""
        from storage import tournament_rules  # Import here to avoid circular import
        await display_rules(interaction, tournament_rules)


async def display_rules(interaction: discord.Interaction, tournament_rules: dict):
    """Display current tournament rules in an embed"""
    try:
        current_rules = get_current_rules()
        
        if not current_rules:
            embed = discord.Embed(
                title="📋 Tournament Rules",
                description="No tournament rules have been set yet.",
                color=discord.Color.orange(),
                timestamp=discord.utils.utcnow()
            )
            embed.set_footer(text=TOURNAMENT_SYSTEM_NAME)
        else:
            embed = discord.Embed(
                title="📋 Tournament Rules",
                description=current_rules,
                color=discord.Color.blue(),
                timestamp=discord.utils.utcnow()
            )
            
            # Add metadata if available
            if 'rules' in tournament_rules and 'last_updated' in tournament_rules['rules']:
                updated_by = tournament_rules['rules'].get('updated_by', {}).get('username', 'Unknown')
                embed.set_footer(text=f"{ORGANIZATION_NAME} • Last updated by {updated_by}")
        
        await interaction.response.send_message(embed=embed, ephemeral=False)
        
    except Exception as e:
        print(f"Error displaying rules: {e}")
        await interaction.response.send_message("❌ An error occurred while displaying rules.", ephemeral=False)

