"""
Copyright 2019 kivou.2000607@gmail.com

This file is part of yata.

    yata is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    any later version.

    yata is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with yata. If not, see <https://www.gnu.org/licenses/>.
"""
from django.core.cache import cache

from player.models import Message


def sectionMessage(request):
    section = request.get_full_path().split("/")[1]
    sm = cache.get("context_processor_message")
    if sm is None:
        print("[context_processor] cache message")
        sm = []
        for m in Message.objects.order_by("-pk"):
            sm.append([m.section, m.message, m.level])
        cache.set("context_processor_message", sm, 3600)

    return {"sectionMessages": [m for m in sm if m[0] in [section, "all"]]}

