# $Id$
# encoding: utf-8
"""holidaymsgr.holidays.testing_views"""
__author__ = 'Richard Mitchell <richard.mitchell@isotoma.com>'
__docformat__ = 'restructuredtext en'
__version__ = '$Revision$'[11:-2]

import email.header
import email.message
import imaplib
import smtplib
import time
import uuid

from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render
import sievelib.managesieve

from holidaymsgr.holidays import forms
from holidaymsgr.holidays import views

LOGIN_TEMPLATE = 'holidays/test_login.html'
TEST_TEMPLATE = 'holidays/test.html'
CURRENT_TESTS = {}
TESTS = [{
    'name': 'Test',
    'message': 'foo',
    'headers': [],
    'subject': 'bar',
    'test': lambda subject, body: 'OK',
    }, {
    'name': 'Test List-Help',
    'message': 'foo',
    'headers': [('List-Help', 'Foo')],
    'subject': 'bar',
    'test': lambda subject, body: 'Failed',
    'timeout': 'Success',
    }, {
    'name': 'Test List-Unsubscribe',
    'message': 'foo',
    'headers': [('List-Unsubscribe', 'Foo')],
    'subject': 'bar',
    'test': lambda subject, body: 'Failed',
    'timeout': 'Success',
    }, {
    'name': 'Test List-Subscribe',
    'message': 'foo',
    'headers': [('List-Subscribe', 'Foo')],
    'subject': 'bar',
    'test': lambda subject, body: 'Failed',
    'timeout': 'Success',
    }, {
    'name': 'Test List-Owner',
    'message': 'foo',
    'headers': [('List-Owner', 'Foo')],
    'subject': 'bar',
    'test': lambda subject, body: 'Failed',
    'timeout': 'Success',
    }, {
    'name': 'Test List-Post',
    'message': 'foo',
    'headers': [('List-Post', 'Foo')],
    'subject': 'bar',
    'test': lambda subject, body: 'Failed',
    'timeout': 'Success',
    }, {
    'name': 'Test List-Archive',
    'message': 'foo',
    'headers': [('List-Archive', 'Foo')],
    'subject': 'bar',
    'test': lambda subject, body: 'Failed',
    'timeout': 'Success',
    }, {
    'name': 'Test List-Id',
    'message': 'foo',
    'headers': [('List-Id', 'Foo')],
    'subject': 'bar',
    'test': lambda subject, body: 'Failed',
    'timeout': 'Success',
    }, {
    'name': 'Test Mailing-List',
    'message': 'foo',
    'headers': [('Mailing-List', 'Foo')],
    'subject': 'bar',
    'test': lambda subject, body: 'Failed',
    'timeout': 'Success',
    }, {
    'name': 'Test Precedence normal',
    'message': 'foo',
    'headers': [('Precedence', 'normal')],
    'subject': 'bar',
    'test': lambda subject, body: 'OK',
    'timeout': 'Timed out',
    }, {
    'name': 'Test Precedence list',
    'message': 'foo',
    'headers': [('Precedence', 'list')],
    'subject': 'bar',
    'test': lambda subject, body: 'Failed',
    'timeout': 'Success',
    }, {
    'name': 'Test Precedence bulk',
    'message': 'foo',
    'headers': [('Precedence', 'bulk')],
    'subject': 'bar',
    'test': lambda subject, body: 'Failed',
    'timeout': 'Success',
    }, {
    'name': 'Test Precedence junk',
    'message': 'foo',
    'headers': [('Precedence', 'junk')],
    'subject': 'bar',
    'test': lambda subject, body: 'Failed',
    'timeout': 'Success',
    }, {
    'name': 'Test Precedence LIST',
    'message': 'foo',
    'headers': [('Precedence', 'LIST')],
    'subject': 'bar',
    'test': lambda subject, body: 'Failed',
    'timeout': 'Success',
    }, {
    'name': 'Test Precedence BULK',
    'message': 'foo',
    'headers': [('Precedence', 'BULK')],
    'subject': 'bar',
    'test': lambda subject, body: 'Failed',
    'timeout': 'Success',
    }, {
    'name': 'Test Precedence JUNK',
    'message': 'foo',
    'headers': [('Precedence', 'JUNK')],
    'subject': 'bar',
    'test': lambda subject, body: 'Failed',
    'timeout': 'Success',
    }, {
    'name': 'Test to Multiple recipients of',
    'message': 'foo',
    'headers': [('To', 'Multiple recipients of baz')],
    'subject': 'bar',
    'test': lambda subject, body: 'Failed',
    'timeout': 'Success',
    }, {
    'name': 'Test to Multiple RECIPIENTS of',
    'message': 'foo',
    'headers': [('To', 'Multiple RECIPIENTS of baz')],
    'subject': 'bar',
    'test': lambda subject, body: 'Failed',
    'timeout': 'Success',
    }]
TEST_SCRIPT_VARIABLES = {
    'subject': u'{original_subject}: \u2603 IT\'S CHRISTMAS!',
    'email_address': u'{email}',
    'message': u'\u2603. Merry Christmas and a Happy New Year.',
    'handle': u'{handle}',
    }
TEST_SCRIPT = views._make_script(**TEST_SCRIPT_VARIABLES)
TIMEOUT = 15


def _enable_disable(username, password):
    sieve_client = sievelib.managesieve.Client(settings.SIEVE_SERVER_HOST,
                                               settings.SIEVE_SERVER_PORT)
    sieve_client.connect(username, password)
    active_script, _others = sieve_client.listscripts()
    sieve_client.setactive('')
    sieve_client.setactive(active_script)


def _get_active_script(username, password):
    sieve_client = sievelib.managesieve.Client(settings.SIEVE_SERVER_HOST,
                                               settings.SIEVE_SERVER_PORT)
    sieve_client.connect(username, password)
    active_script, _others = sieve_client.listscripts()
    script = sieve_client.getscript(active_script)
    return active_script, script


def _set_active_script(username, password, script_name, script,
                       delete_active=False):
    sieve_client = sievelib.managesieve.Client(settings.SIEVE_SERVER_HOST,
                                               settings.SIEVE_SERVER_PORT)
    sieve_client.connect(username, password)
    active_script, _others = sieve_client.listscripts()
    sieve_client.setactive('')
    if delete_active:
        sieve_client.deletescript(active_script)
    sieve_client.putscript(script_name, script)
    sieve_client.setactive(script_name)


def _send_message(test_id, part_number, username, password, sender, recipient,
                  headers, subject, body, cls=smtplib.SMTP):
    if settings.SMTP_SERVER_SSL and cls is smtplib.SMTP:
        # Only set the SSL class if the default is not already overridden
        cls = smtplib.SMTP_SSL

    conn = cls(settings.SMTP_SERVER_HOST, settings.SMTP_SERVER_PORT)
    conn.ehlo_or_helo_if_needed()
    if settings.SMTP_SERVER_STARTTLS:
        conn.starttls()
        conn.ehlo_or_helo_if_needed()

    if settings.SMTP_SERVER_HOST not in ('127.0.0.1', 'localhost', '::1'):
        try:
            conn.login(username, password)
        except smtplib.SMTPResponseException:
            CURRENT_TESTS[test_id]['error'] = \
                'Could not authenticate to send message'

    message = email.message.Message()
    message.set_charset('UTF8')
    for header_key, header_value in headers:
        encoded_header_value = str(email.header.Header(header_value, 'UTF8'))
        message.add_header(header_key, encoded_header_value)

    encoded_subject = str(email.header.Header(subject, 'UTF8'))
    encoded_sender = str(email.header.Header(sender, 'UTF8'))
    encoded_recipient = str(email.header.Header(recipient, 'UTF8'))
    message.add_header('Subject', encoded_subject)
    message.add_header('From', encoded_sender)
    message.add_header('To', encoded_recipient)
    message.set_type('text/plain')
    message.set_param('charset', 'UTF8')
    message.set_payload(body, 'UTF8')

    refused = conn.sendmail(sender, [recipient], message.as_string())
    if refused:
        CURRENT_TESTS[test_id]['error'] = 'Recipient refused.'
    conn.quit()


def decode_header(header_str):
    result = u''
    for part_str, part_enc in email.header.decode_header(header_str):
        result += part_str.decode(part_enc)

    return result


def check_mail(conn, timeout, test_id, part_num, run_test=False):
    start = time.time()
    test_name = TESTS[part_num]['name']
    search_terms = '(SUBJECT "{test_id}:{part_num}")'.format(
                        test_id=test_id.replace('"', '\\"'),
                        part_num=str(part_num),
                    )
    while (time.time() < (start + timeout) and
           not CURRENT_TESTS[test_id].get('completed', False)):

        _status, data = conn.search(None, search_terms)
        msg_ids = data[0].split()
        for msg_id in msg_ids:
            data = conn.fetch(msg_id, '(BODY.PEEK[])')[1]
            _msg_part, part = data[0]

            msg = email.message_from_string(part)
            subject = decode_header(msg.get('Subject'))
            subj_test_id, part_number, subject_string = \
                subject.split(':', 3)
            part_number = int(part_number)
            if part_number != part_num:
                continue
            if subj_test_id != test_id:
                continue
            if run_test:
                body = msg.get_payload(decode=True)
                test_result = TESTS[part_number]['test'](subject_string, body)
                CURRENT_TESTS[test_id]['tests'][test_name] = test_result
            break

        time.sleep(1)

    conn.close()
    conn.logout()

    if time.time() >= (start + timeout):
        CURRENT_TESTS[test_id]['tests'][test_name] = \
            TESTS[part_num].get('timeout', 'Timed out')


def _receive_test_reply(test_id, part_num, username, password,
                        timeout=TIMEOUT, cls=imaplib.IMAP4):
    def check_reply(*args, **kwargs):
        kwargs['run_test'] = True
        return check_mail(*args, **kwargs)

    return _receive_test_message(test_id, part_num, username, password,
                                 timeout, cls, check_mail=check_reply)


def _receive_test_message(test_id, part_num, username, password,
                          timeout=TIMEOUT, cls=imaplib.IMAP4,
                          check_mail=check_mail):
    if settings.IMAP_SERVER_SSL and cls is imaplib.IMAP4:
        # Only set the SSL class if the default is not already overridden
        cls = imaplib.IMAP4_SSL

    conn = cls(settings.IMAP_SERVER_HOST, settings.IMAP_SERVER_PORT)
    try:
        conn.login(username, password)
    except cls.error:
        CURRENT_TESTS[test_id]['error'] = 'Could not authenticate.'

    conn.select()

    check_mail(conn, timeout, test_id, part_num)


def test_view(request):
    if not request.session.get('test_authenticated', False):
        return HttpResponseRedirect('/test_login')

    email = request.session['email']
    test_id = uuid.uuid4().hex
    active_script_name, active_script = \
        _get_active_script(request.session['username'],
                           request.session['password'])

    test_script = TEST_SCRIPT.replace('{email}', views._sieve_quote(email))
    CURRENT_TESTS[test_id] = {
        'error': None,
        'completed': False,
        'tests': [],
        }
    CURRENT_TESTS[test_id]['tests'] = \
        dict([(t['name'], t.get('default', 'Timed out')) for t in TESTS])
    i = 0
    for test in TESTS:
        headers = test['headers']
        subject = ':'.join([test_id, str(i), test['subject']])
        message = test['message']
        # Need to reset the script after every test, to give it a different
        # handle,otherwise our address is cached and won't be auto-replied to
        # after the first one. Also we want to include the test number in the
        # response subject line.
        _set_active_script(
               request.session['username'],
               request.session['password'],
               test_id,
               test_script.replace(
                        '{original_subject}', views._sieve_quote(subject)
                    ).replace(
                        '{handle}', views._sieve_quote(test_id + str(i))
                    ),
               delete_active=bool(i)
            )
        _send_message(test_id,
                      i,
                      request.session['test_username'],
                      request.session['test_password'],
                      request.session['test_email'],
                      request.session['email'],
                      headers,
                      subject,
                      message,)

        _receive_test_message(test_id, i,
                              request.session['username'],
                              request.session['password'])

        _receive_test_reply(test_id, i,
                            request.session['test_username'],
                            request.session['test_password'])
        i += 1

    _set_active_script(request.session['username'],
                       request.session['password'],
                       active_script_name,
                       active_script or '',
                       delete_active=bool(TESTS))

    return render(request, TEST_TEMPLATE, CURRENT_TESTS[test_id])


def _validate_imap_credentials(username, password, cls=imaplib.IMAP4):
    if settings.IMAP_SERVER_SSL and cls is imaplib.IMAP4:
        # Only set the SSL class if the default is not already overridden
        cls = imaplib.IMAP4_SSL

    conn = cls(settings.IMAP_SERVER_HOST, settings.IMAP_SERVER_PORT)
    try:
        conn.login(username, password)
    except cls.error:
        return cls.error
    finally:
        conn.logout()
    return None


def test_login(request, form_cls=forms.LoginForm, render=render,
          validator=_validate_imap_credentials):
    login = form_cls()
    if not request.session.get('authenticated', False):
        return HttpResponseRedirect('/')

    error = None
    if request.method == 'POST':
        login = form_cls(request.POST, error_class=views.SimpleErrorList)
        if login.is_valid():  # All validation rules pass
            request.session['test_email'] = login.cleaned_data['email']
            request.session['test_username'] = login.cleaned_data['username']
            request.session['test_password'] = login.cleaned_data['password']
            request.session['test_authenticated'] = False
            error = validator(request.session['test_username'],
                              request.session['test_password'])
            if error is not None:
                print error
            else:
                request.session['test_authenticated'] = True
                return HttpResponseRedirect('test')

    return render(request, LOGIN_TEMPLATE, {
        'test_login': login,
        'error_message': error
    })
