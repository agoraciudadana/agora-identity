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

from django.views.generic import TemplateView, FormView
from django.conf import settings
from django.shortcuts import redirect
from django.utils.crypto import constant_time_compare, salted_hmac

from forms import RegisterForm

def check_hmac(hmac, value):
    '''
    Checks the hmac
    '''
    hmac_calculated = salted_hmac(key_salt=settings.LOGIN_HMAC_SALT,
                                  value=value,
                                  secret=settings.LOGIN_HMAC_SECRET)
    return constant_time_compare(hmac, hmac_calculated.hexdigest())

class AuthView(FormView):
    '''
    Default view for the root
    '''
    template_name = 'base/auth.html'
    form_class = RegisterForm

    def get_context_data(self, **kwargs):
        context = super(AuthView, self).get_context_data(**kwargs)
        context['EVENT_TITLE'] = settings.EVENT_TITLE
        context['EVENT_TEXT'] = settings.EVENT_TEXT
        context['TOS_TITLE'] = settings.TOS_TITLE
        context['TOS_TEXT'] = settings.TOS_TEXT
        return context

    def get_success_url(self):
        # TODO
        return ''

    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        form.send()
        return super(AuthView, self).form_valid(form)


    def dispatch(self, *args, **kwargs):
        self.kwargs = kwargs
        hmac = self.kwargs["hmac"]
        email = self.kwargs["email"]

        # authenticate the link
        if not check_hmac(hmac, email):
            return redirect('invalid-auth')

        return super(AuthView, self).dispatch(*args, **kwargs)


class InvalidAuthView(TemplateView):
    template_name = 'base/invalid_auth.html'

    def get_context_data(self, **kwargs):
        context = super(InvalidAuthView, self).get_context_data(**kwargs)
        context['AGORA_LINK'] = settings.AGORA_LINK
        context['CONTACT_MAIL'] = "mailto:" + settings.DEFAULT_FROM_EMAIL
        return context
