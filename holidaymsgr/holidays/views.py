# encoding: utf-8

import codecs
import os.path

from django.forms.util import ErrorList
from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import  render

from django.views.decorators.debug import sensitive_post_parameters, sensitive_variables

import pkg_resources
import sievelib.managesieve
import sievelib.parser

from holidaymsgr.holidays import forms


AWAY_TEMPLATE_PATH = os.path.abspath(
    pkg_resources.resource_filename(  # @UndefinedVariable
        'holidaymsgr',
         os.path.join('holidays', 'sieve', 'away.sieve')
         )
    )
AWAY_TEMPLATE = codecs.open(AWAY_TEMPLATE_PATH, 'r', 'utf8').read()
SCRIPT_NAME = 'holidaymessage'
INDEX_TEMPLATE = 'holidays/index.html'
MESSAGE_TEMPLATE = 'holidays/message.html'


class SimpleErrorList(ErrorList):

    def __unicode__(self):
        return self.as_divs()

    def as_divs(self):
        if not self:
            return u''

        return u''.join(map(unicode, self))


def _validate_sieve_credentials(username, password,
                               client_cls=sievelib.managesieve.Client):
    sieve_client = client_cls(settings.SIEVE_SERVER_HOST,
                              settings.SIEVE_SERVER_PORT)
    try:
        sieve_client.connect(username, password)
    except sievelib.managesieve.Error, e:
        return e

    return None


@sensitive_post_parameters("password")
def index(request, form_cls=forms.LoginForm, render=render,
          validator=_validate_sieve_credentials):
    login = form_cls()
    error = None
    if request.method == 'POST':
        login = form_cls(request.POST, error_class=SimpleErrorList)
        if login.is_valid():  # All validation rules pass
            request.session['email'] = login.cleaned_data['email']
            request.session['username'] = login.cleaned_data['username']
            request.session['password'] = login.cleaned_data['password']
            request.session['authenticated'] = False
            error = validator(request.session['username'],
                              request.session['password'])
            if error is not None:
                print error
            else:
                request.session['authenticated'] = True
                return HttpResponseRedirect('message')

    return render(request, INDEX_TEMPLATE, {
        'login': login,
        'error_message': error
    })


def _sieve_quote(term):
    # RFC 5228 §2.4.2.
    term = term.replace(u'\\', u'\\\\').replace(u'"', u'\\"')
    return u'"{term}"'.format(term=term)


def _make_script(email_address, subject, message, days, handle=SCRIPT_NAME,
                 template=AWAY_TEMPLATE):
    return template.format(contents=_sieve_quote(message),
                           subject=_sieve_quote(subject),
                           handle=_sieve_quote(handle),
                           days=str(days),
                           email=_sieve_quote(email_address))


def _write_and_activate_script(sieve_client, script,
                             parser_cls=sievelib.parser.Parser):
    parser = parser_cls()

    # assert script is valid
    assert parser.parse(script)

    if not sieve_client.havespace(SCRIPT_NAME, len(script)):
        raise RuntimeError('No space left on server for new script.')
    else:
        if not sieve_client.putscript(SCRIPT_NAME, script):
            raise RuntimeError('Unable to write script.')
        if not sieve_client.setactive(SCRIPT_NAME):
            raise RuntimeError('Unable to activate script.')


def _activate(request, sieve_client, form_cls=forms.MailForm,
              make_script=_make_script,
              set_script=_write_and_activate_script):
    mail_form = form_cls(request.POST, error_class=SimpleErrorList)
    if mail_form.is_valid():
        message = mail_form.cleaned_data['message']
        subject = mail_form.cleaned_data['subject']
        days = mail_form.cleaned_data['days']
        email_address = request.session['email']

        script = make_script(email_address, subject, message, days)
        set_script(sieve_client, script)

    return mail_form


def _is_holiday_script_active(sieve_client):
    active_script, _others = sieve_client.listscripts()
    if active_script == u"ingo":
        sieve_client.setactive(u'')
        active_script = u''

    return active_script == SCRIPT_NAME

@sensitive_variables("password")
def message(request, form_cls=forms.MailForm,
            client_cls=sievelib.managesieve.Client,
            activate=_activate, is_active=_is_holiday_script_active,
            render=render):
    if not request.session.get('authenticated', False):
        return HttpResponseRedirect('/')

    mail_form = form_cls()
    sieve_client = client_cls(settings.SIEVE_SERVER_HOST,
                              settings.SIEVE_SERVER_PORT)
    active = False
    username = request.session['username']
    password = request.session['password']
    try:
        sieve_client.connect(username, password)
    except sievelib.managesieve.Error:
        request.session['authenticated'] = False
        del request.session['username']
        del request.session['password']
        return HttpResponseRedirect('/')

    try:
        if request.method == 'POST':
            if 'set_away_message' in request.POST:
                mail_form = activate(request, sieve_client)
            elif 'deactivate' in request.POST:
                sieve_client.setactive('')

        active = is_active(sieve_client)

    except sievelib.managesieve.Error:
        # TODO
        pass

    return render(request, MESSAGE_TEMPLATE, {
        'message_active': active,
        'mail': mail_form
    })
