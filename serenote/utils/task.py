"""Contains the Task class."""

import discord

from serenote import db


class Task:
    """Task class to handle all the work of managing a task."""

    icons = lambda img: f"https://raw.githubusercontent.com/LeptoFlare/serenote/main/static/{img}.png"
    actions = {
        "complete": 762882665274933248,
    }

    @classmethod
    async def create_task(cls, ctx, title, description=discord.Embed.Empty):
        """Create a new task and return associated Task object."""
        # Create embed
        embed = discord.Embed(
            title=title,
            description=description,
            color=discord.Color.blurple())
        cls.set_complete(embed, False)
        # Send task embed
        message = await ctx.send(embed=embed)
        # Add actions
        for action in cls.actions.values():
            react = await ctx.bot.get_emoji(action)
            await message.add_reaction(react)

        # Insert task into database
        db_task = db.Task(message_id=ctx.message.id, author_id=ctx.author.id)
        db_task.save()

        # Build task object
        return Task(message, db_task)
    
    def __init__(self, message, db):
        self.message = message
        self.db = db
        self.embed = self.message.embeds[0]

    async def action(self, payload, reaction_add: bool):
        """Validate payload and run a task action."""
        if payload.user_id != self.db.author_id:
            return
        await {
            'complete': self.complete,
        }[payload.emoji.name](reaction_add)

    async def complete(self, checked: bool):
        """Action task complete as checked value."""
        await self.message.edit(embed=self.set_complete(self.embed, checked))

    @classmethod
    def set_complete(cls, embed, checked: bool):
        embed.set_author(**{
            False: {"name": "Incomplete Task", "icon_url": cls.icons("unchecked")},
            True: {"name": "Completed Task", "icon_url": cls.icons("checked")},
        }[checked])
        return embed
