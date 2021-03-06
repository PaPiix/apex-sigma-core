﻿# Apex Sigma: The Database Giant Discord Bot.
# Copyright (C) 2018  Lucia's Cipher
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import arrow
import discord

from sigma.core.mechanics.event import SigmaEvent
from sigma.core.utilities.data_processing import user_avatar
from sigma.core.utilities.event_logging import log_event
from sigma.modules.moderation.server_settings.filters.cleaners import clean_content
from sigma.modules.moderation.warning.issuewarning import warning_data


async def send_word_blocker(ev: SigmaEvent, message: discord.Message):
    if message.guild:
        if isinstance(message.author, discord.Member):
            is_owner = message.author.id in ev.bot.cfg.dsc.owners
            if not message.author.permissions_in(message.channel).administrator or is_owner:
                prefix = await ev.db.get_prefix(message)
                if not message.content.startswith(prefix):
                    text = clean_content(message.content.lower())
                    elements = text.split(' ')
                    blocked_words = await ev.db.get_guild_settings(message.guild.id, 'BlockedWords') or []
                    hard_blocked_words = await ev.db.get_guild_settings(message.guild.id, 'HardBlockedWords') or []
                    remove = False
                    reason = None
                    for word in blocked_words:
                        if word in elements:
                            remove = True
                            reason = word
                            break
                    for word in hard_blocked_words:
                        if word in message.content:
                            remove = True
                            reason = word
                    if remove:
                        try:
                            filter_warn = await ev.db.get_guild_settings(message.guild.id, 'FilterAutoWarn')
                            if filter_warn:
                                warn_data = warning_data(message.guild.me, message.author, f'Said "{reason}".')
                                await ev.db[ev.db.db_nam].Warnings.insert_one(warn_data)
                            await message.delete()
                            title = f'🔥 Your message was deleted for containing "{reason}".'
                            to_author = discord.Embed(color=0xFFCC4D, title=title)
                            try:
                                await message.author.send(embed=to_author)
                            except discord.Forbidden:
                                pass
                            author = f'{message.author.name}#{message.author.discriminator}'
                            title = f'I deleted {author}\'s message for containing "{reason}".'
                            log_embed = discord.Embed(color=0xFFCC4D, timestamp=arrow.utcnow().datetime)
                            log_embed.description = f'Content: {message.content}'
                            log_embed.set_author(name=title, icon_url=user_avatar(message.author))
                            log_embed.set_footer(text=f'Channel: #{message.channel.name} [{message.channel.id}]')
                            await log_event(ev.bot, message.guild, ev.db, log_embed, 'LogFilters')
                        except discord.ClientException:
                            pass
