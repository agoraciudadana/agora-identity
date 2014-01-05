# -*- coding: utf-8 -*-
# Copyright (C) 2014 Eduardo Robles Elvira <edulix AT agoravoting DOT com>
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

#
# Forms for the base application
#

from django import forms
from django.conf import settings

import json
import requests
from uuid import uuid4


class RegisterForm(forms.Form):
    name = forms.CharField(max_length=140, required=True)
    password = forms.CharField(required=True)
    password2 = forms.CharField(required=True)

    def __init__(self, *args, **kwargs):
        self.request = kwargs['request']
        self.email = kwargs['email']
        del kwargs['request']
        del kwargs['email']
        super(RegisterForm, self).__init__(*args, **kwargs)

    def clean_password(self):
        if self.cleaned_data['password'] != self.data['password2'] or\
                len(self.cleaned_data['password']) <= 3:
            raise forms.ValidationError(_('The two password fields'
                ' didn\'t match or are insecure.'))
        return self.cleaned_data['password']

    def register(self):
        '''
        Register the user and returns the activation url
        '''
        url = settings.AGORA_URL + "/api/v1/user/register/"

        headers = {
            'content-type': 'application/json',
            'Authorization': settings.AGORA_API_KEY
        }

        # random username, until it's available the username or any other
        # kind of error appears. Don't try endlessly though
        j = dict()
        for i in range(0, 5):
            username = settings.BASE_USERNAME + str(uuid4())[:settings.NUM_RANDOM_USERNAME_CHARS]
            payload = dict(
                first_name=self.cleaned_data['name'],
                username=username,
                password1=self.cleaned_data['password'],
                password2=self.cleaned_data['password'],
                email=self.email,
                activation_secret=settings.AGORA_SECRET
            )
            r = requests.post(url, data=json.dumps(payload), verify=False,
                              headers=headers)

            try:
                j = r.json()
                assert isinstance(j, dict)
            except:
                break
            if r.status_code != 400 or "username" not in j:
                break

        # maybe we tried hard, but didn't find any username available. strange,
        # but could happen I guess if we are lucky and get lots of new users!
        if r.status_code == 400 and isinstance(j, dict) and\
                "username" in j:
            raise Exception("error trying to find an available username")

        # maybe there was other kind of error going on
        if r.status_code != 200:
            raise Exception("error registering the user. Something strange is "
                            "going on")

        # if this triggers an error so be it.. it shouldn't
        return r.json()['activation_url']
