# -*- coding: utf-8 -*-
# Copyright (C) 2014 Eduardo Robles Elvira <edulix AT gmail DOT com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from django.conf import settings
from django.utils.translation import get_language
import json

import sys

def base(request):
    '''
    This is a context processor that adds some vars to the base template
    '''
    return {
        'SITE_NAME': settings.SITE_NAME,
        'languages': json.dumps(
            dict(
                current=get_language(),
                objects=[dict(lang_code=lang_code, name=unicode(name)) for lang_code, name in settings.LANGUAGES]
            )
        ),
    }
