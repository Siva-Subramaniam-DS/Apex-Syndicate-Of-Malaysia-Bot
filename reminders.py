"""
Event reminders and scheduling module for the ASM Tournament Bot
Handles 10-minute reminders and event cleanup tasks
"""

import discord
import datetime
import asyncio
import pytz
import os
from typing import Optional
from storage import scheduled_events, save_scheduled_events
from utils import reminder_tasks, cleanup_tasks


async def send_ten_minute_reminder(event_id: str, team1_captain: discord.Member, team2_captain: discord.Member, judge: Optional[discord.Member], event_channel: discord.TextChannel, match_time: datetime.datetime):
    """Send 10-minute reminder notification to judge and captains"""
    try:
        if not event_channel:
            print(f"No event channel provided for event {event_id}")
            return

        # Get the latest judge from scheduled_events if available
        resolved_judge = judge
        if event_id in scheduled_events:
            stored_judge = scheduled_events[event_id].get('judge')
            if stored_judge:
                resolved_judge = stored_judge

        # Create reminder embed
        embed = discord.Embed(
            title="⏰ 10-MINUTE MATCH REMINDER",
            description=f"**Your tournament match is starting in 10 minutes!**",
            color=discord.Color.orange(),
            timestamp=discord.utils.utcnow()
        )
        embed.add_field(name="🕒 Match Time", value=f"<t:{int(match_time.timestamp())}:F>", inline=False)
        embed.add_field(name="👥 Team Captains", value=f"{team1_captain.mention} vs {team2_captain.mention}", inline=False)
        if resolved_judge:
            embed.add_field(name="👨‍⚖️ Judge", value=f"{resolved_judge.mention}", inline=False)
        embed.add_field(name="⚡ Action Required", value="Please prepare for the match and join the designated channel.", inline=False)
        embed.set_footer(text="Tournament Management System")

        # Send notification with pings
        pings = f"{team1_captain.mention} {team2_captain.mention}"
        if resolved_judge:
            pings = f"{resolved_judge.mention} " + pings
        notification_text = f"🔔 **MATCH REMINDER**\n\n{pings}\n\nYour match starts in **10 minutes**!"

        await event_channel.send(content=notification_text, embed=embed)
        print(f"10-minute reminder sent for event {event_id}")
    except Exception as e:
        print(f"Error sending 10-minute reminder for event {event_id}: {e}")


async def schedule_ten_minute_reminder(event_id: str, team1_captain: discord.Member, team2_captain: discord.Member, judge: Optional[discord.Member], event_channel: discord.TextChannel, match_time: datetime.datetime):
    """Schedule a 10-minute reminder for the match"""
    try:
        # Calculate when to send the 10-minute reminder
        reminder_time = match_time - datetime.timedelta(minutes=10)
        now = datetime.datetime.now(pytz.UTC)

        # Ensure match_time and reminder_time are timezone-aware UTC
        if match_time.tzinfo is None:
            match_time = match_time.replace(tzinfo=pytz.UTC)
            reminder_time = match_time - datetime.timedelta(minutes=10)

        # Check if reminder time is in the future
        if reminder_time <= now:
            print(f"Reminder time for event {event_id} is in the past, skipping")
            return

        # Calculate delay in seconds
        delay_seconds = (reminder_time - now).total_seconds()

        async def reminder_task():
            try:
                await asyncio.sleep(delay_seconds)
                await send_ten_minute_reminder(event_id, team1_captain, team2_captain, judge, event_channel, match_time)
            except asyncio.CancelledError:
                print(f"Reminder task for event {event_id} was cancelled")
            except Exception as e:
                print(f"Error in reminder task for event {event_id}: {e}")

        # Cancel existing reminder if any
        if event_id in reminder_tasks:
            reminder_tasks[event_id].cancel()

        # Schedule new reminder
        reminder_tasks[event_id] = asyncio.create_task(reminder_task())
        print(f"10-minute reminder scheduled for event {event_id} at {reminder_time}")
    except Exception as e:
        print(f"Error scheduling 10-minute reminder for event {event_id}: {e}")


async def schedule_event_reminder_v2(event_id: str, team1_captain: discord.Member, team2_captain: discord.Member, judge: Optional[discord.Member], event_channel: discord.TextChannel):
    """Schedule event reminder with 10-minute notification using stored event datetime"""
    try:
        if event_id not in scheduled_events:
            print(f"Event {event_id} not found in scheduled_events")
            return
        event_data = scheduled_events[event_id]
        match_time = event_data.get('datetime')
        if not match_time:
            print(f"No datetime found for event {event_id}")
            return
        # Ensure timezone-aware UTC
        if match_time.tzinfo is None:
            match_time = match_time.replace(tzinfo=pytz.UTC)
        await schedule_ten_minute_reminder(event_id, team1_captain, team2_captain, judge, event_channel, match_time)
    except Exception as e:
        print(f"Error in schedule_event_reminder_v2 for event {event_id}: {e}")


async def schedule_event_cleanup(event_id: str, delay_hours: int = 24, bot=None):
    """Schedule cleanup to remove an event after delay_hours (default 24h)."""
    try:
        if event_id not in scheduled_events:
            return
        delay_seconds = delay_hours * 3600

        async def cleanup_task():
            try:
                await asyncio.sleep(delay_seconds)
                data = scheduled_events.get(event_id)
                if not data:
                    return
                # Delete original schedule message if known
                try:
                    if bot:
                        guilds = bot.guilds
                        for guild in guilds:
                            ch_id = data.get('schedule_channel_id')
                            msg_id = data.get('schedule_message_id')
                            if ch_id and msg_id:
                                channel = guild.get_channel(ch_id)
                                if channel:
                                    try:
                                        msg = await channel.fetch_message(msg_id)
                                        await msg.delete()
                                    except discord.NotFound:
                                        pass
                                    except Exception as e:
                                        print(f"Error deleting schedule message for {event_id}: {e}")
                except Exception as e:
                    print(f"Guild/channel fetch error during cleanup for {event_id}: {e}")

                # Clean up poster file if any
                try:
                    poster_path = data.get('poster_path')
                    if poster_path and os.path.exists(poster_path):
                        os.remove(poster_path)
                except Exception as e:
                    print(f"Poster cleanup error for {event_id}: {e}")

                # Remove any reminder task
                try:
                    if event_id in reminder_tasks:
                        reminder_tasks[event_id].cancel()
                        del reminder_tasks[event_id]
                except Exception:
                    pass

                # Finally remove from scheduled events and persist
                try:
                    if event_id in scheduled_events:
                        del scheduled_events[event_id]
                        save_scheduled_events()
                except Exception as e:
                    print(f"Error removing event {event_id} in cleanup: {e}")
            except asyncio.CancelledError:
                print(f"Cleanup task for event {event_id} was cancelled")
            except Exception as e:
                print(f"Error in cleanup task for event {event_id}: {e}")

        # Cancel existing cleanup if any and schedule new
        if event_id in cleanup_tasks:
            try:
                cleanup_tasks[event_id].cancel()
            except Exception:
                pass

        cleanup_tasks[event_id] = asyncio.create_task(cleanup_task())
        print(f"Cleanup scheduled for event {event_id} in {delay_hours} hours")
    except Exception as e:
        print(f"Error scheduling cleanup for event {event_id}: {e}")

