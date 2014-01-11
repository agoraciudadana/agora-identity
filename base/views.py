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
# Views for the base application
#

import requests
import json
import urllib

from django.views.generic import TemplateView, FormView
from django.core.urlresolvers import reverse
from django.conf import settings
from django.core.validators import validate_email
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.utils.crypto import constant_time_compare, salted_hmac

from forms import RegisterForm, SendMailsForm

def check_hmac(hmac, value):
    '''
    Checks the hmac
    '''
    hmac_calculated = salted_hmac(key_salt=settings.LOGIN_HMAC_SALT,
                                  value=value,
                                  secret=settings.LOGIN_HMAC_SECRET)
    print("hmac_calculated = /auth/%s/%s" % (hmac_calculated.hexdigest(), value))
    return constant_time_compare(hmac, hmac_calculated.hexdigest())



def generate_hmac(value):
    '''
    Generates the hmac
    '''
    return salted_hmac(key_salt=settings.LOGIN_HMAC_SALT, value=value,
                       secret=settings.LOGIN_HMAC_SECRET).hexdigest()

class AuthView(FormView):
    '''
    Default view for the root
    '''
    template_name = 'base/auth.html'
    form_class = RegisterForm

    def get_form_kwargs(self):
        kwargs = super(AuthView, self).get_form_kwargs()
        kwargs.update({'request': self.request, 'email': self.email})
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(AuthView, self).get_context_data(**kwargs)
        context['EVENT_TITLE'] = settings.EVENT_TITLE
        context['EVENT_TEXT'] = settings.EVENT_TEXT
        context['TOS_TITLE'] = settings.TOS_TITLE
        context['TOS_TEXT'] = settings.TOS_TEXT
        context['email'] = self.email
        return context

    def get_success_url(self):
        '''
        Redirect to the activation url
        '''
        return settings.AGORA_URL + self.url

    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        self.url = form.register()
        return super(AuthView, self).form_valid(form)

    def dispatch(self, *args, **kwargs):
        self.kwargs = kwargs
        hmac = self.kwargs["hmac"]
        self.email = self.kwargs["email"]

        # check for an invalid email
        try:
            validate_email(self.email)
        except:
            return redirect('invalid-auth')

        # authenticate the link
        if not check_hmac(hmac, self.email):
            return redirect('invalid-auth')

        # try to login with this email/user
        url = settings.AGORA_URL + "/api/v1/user/email_login/"
        payload = dict(
            activation_secret=settings.AGORA_SECRET,
            email=self.email
        )

        headers = {
            'content-type': 'application/json',
            'Authorization': settings.AGORA_API_KEY
        }

        r = requests.post(url, data=json.dumps(payload), verify=False,
                          headers=headers)
        if r.status_code != 200:
            print("r.status_code = %d\n" % r.status_code)
            return super(AuthView, self).dispatch(*args, **kwargs)

        try:
            url = r.json()['url']
        except:
            return super(AuthView, self).dispatch(*args, **kwargs)
        return HttpResponseRedirect(url)


class InvalidAuthView(TemplateView):
    template_name = 'base/invalid_auth.html'

    def get_context_data(self, **kwargs):
        context = super(InvalidAuthView, self).get_context_data(**kwargs)
        context['AGORA_LINK'] = settings.AGORA_URL
        context['CONTACT_MAIL'] = "mailto:" + settings.DEFAULT_FROM_EMAIL
        return context


class SendMailsView(FormView):
    template_name = 'base/send_mails.html'
    form_class = SendMailsForm

    def get_form_kwargs(self):
        kwargs = super(SendMailsView, self).get_form_kwargs()
        kwargs.update({'request': self.request})
        return kwargs

    def get_success_url(self):
        '''
        Redirect to the activation url
        '''
        return reverse('send-mails-success')

    def form_valid(self, form):
        form.send_mails()
        return super(SendMailsView, self).form_valid(form)


class SendMailsSuccessView(TemplateView):
    template_name = 'base/send_mails_success.html'