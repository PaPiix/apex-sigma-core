# Apex Sigma: The Database Giant Discord Bot.
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

import yaml
import aiohttp

from sigma.core.mechanics.event import SigmaEvent


async def dbinit_realdevs(ev: SigmaEvent, force=False):
    doc_count = await ev.db[ev.db.db_nam].RealDevsData.count()
    if not doc_count or force:
        file_url = 'https://gitlab.com/lu-ci/sigma/apex-sigma-res/raw/master/jokes/real_programmers.yml'
        ev.log.info('Updating real developer files.')
        await ev.db[ev.db.db_nam].RealDevsData.drop()
        documents = []
        async with aiohttp.ClientSession() as session:
            async with session.get(file_url) as data_response:
                data = await data_response.read()
                data = yaml.safe_load(data)
        for item in data:
            doc_data = {'content': item}
            documents.append(doc_data)
        await ev.db[ev.db.db_nam].RealDevsData.insert_many(documents)
        ev.log.info('Updated real developer files successfully.')
