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
from django.core.validators import validate_email
from django.utils.crypto import constant_time_compare
from django.core.mail import (EmailMultiAlternatives, EmailMessage, send_mail,
    send_mass_mail, get_connection)
from django.utils.translation import ugettext as _

import json
import requests
import urllib
from uuid import uuid4

def send_mass_html_mail(datatuple, fail_silently=True, user=None, password=None,
                        connection=None):
    """
    Given a datatuple of (subject, text_content, html_content, from_email,
    recipient_list), sends each message to each recipient list. Returns the
    number of emails sent.

    If from_email is None, the DEFAULT_FROM_EMAIL setting is used.
    If auth_user and auth_password are set, they're used to log in.
    If auth_user is None, the EMAIL_HOST_USER setting is used.
    If auth_password is None, the EMAIL_HOST_PASSWORD setting is used.

    """
    connection = connection or get_connection(
        username=user, password=password, fail_silently=fail_silently
    )

    messages = []
    for subject, text, html, from_email, recipient in datatuple:
        message = EmailMultiAlternatives(subject, text, from_email, recipient)
        if len(html) > 0:
            message.attach_alternative(html, 'text/html')
        messages.append(message)

    return connection.send_messages(messages)


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


class SendMailsForm(forms.Form):
    subject = forms.CharField(max_length=140, required=True, min_length=3)
    password = forms.CharField(required=True, min_length=3)
    plaintext_body = forms.CharField(required=True, min_length=10)
    html_body = forms.CharField(required=False, min_length=10)
    receivers = forms.CharField(required=True, min_length=5)

    def __init__(self, *args, **kwargs):
        self.request = kwargs['request']
        del kwargs['request']
        super(SendMailsForm, self).__init__(*args, **kwargs)

    def clean_password(self):
        if not constant_time_compare(settings.SEND_MAILS_PASSWORD,
                                     self.cleaned_data['password']):
            raise forms.ValidationError(_('Invalid password'))
        return self.cleaned_data['password']

    def clean_plaintext_body(self):
        if '##LOGIN_URL##' not in self.cleaned_data['plaintext_body']:
            raise forms.ValidationError(_('No ##LOGIN_URL## inside plaintext '
                                          'body'))
        return self.cleaned_data['plaintext_body']

    def clean_receivers(self):
        lines = self.cleaned_data['receivers'].strip().split('\n')
        emails = []
        for line in lines:
            data = line.split(';')

            if len(data) == 0:
                raise forms.ValidationError(_('empty line'))
            if len(data) > 2:
                raise forms.ValidationError(_('too many semi-colons at '
                                              'line: ' + line))
            if data[0] in emails:
                raise forms.ValidationError(_('repeated email: ' + line))

            try:
                validate_email(data[0].strip())
            except:
                raise forms.ValidationError(_('invalid email: ' + data[0]))

        return self.cleaned_data['receivers']

    def send_mails(self):
        # List of emails to send. tuples are of format:
        #
        # (subject, text, html, from_email, recipient)
        from base.views import generate_hmac
        datatuples = []

        lines = self.cleaned_data['receivers'].split('\n')

        for line in lines:
            data = line.split(';')
            email = data[0]
            name = email
            if len(data) > 1:
                name = data[1].strip()

            quoted_email = urllib.unquote_plus(email)
            iri = '/%sauth/%s/%s' % (settings.LOCATION_SUBPATH,
                                     generate_hmac(email), quoted_email)
            login_url = self.request.build_absolute_uri(iri)

            body = self.cleaned_data['plaintext_body']
            html_body = self.cleaned_data['html_body']
            html_body = html_body.replace('##LOGIN_URL##', login_url)
            html_body = html_body.replace('##EMAIL##', email)
            html_body = html_body.replace('##NAME##', name)
            body = body.replace('##LOGIN_URL##', login_url)
            body = body.replace('##EMAIL##', email)
            body = body.replace('##NAME##', name)

            datatuples.append((
                self.cleaned_data['subject'],
                body,
                html_body,
                None,
                [email]))

        send_mass_html_mail(datatuples)
