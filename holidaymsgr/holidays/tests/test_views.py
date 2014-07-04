# $Id$
# encoding: utf-8
"""holidaymsgr.holidays.tests.test_views"""
__author__ = 'Richard Mitchell <richard.mitchell@isotoma.com>'
__docformat__ = 'restructuredtext en'
__version__ = '$Revision$'[11:-2]

import unittest

import mock

from holidaymsgr.holidays import views


class TestSieveQuote(unittest.TestCase):

    def test_sieve_quote(self):
        self.assertEqual(views._sieve_quote('foo'), '"foo"')

    def test_sieve_quote_squotes(self):
        self.assertEqual(views._sieve_quote("fo'o"), '"fo\'o"')

    def test_sieve_quote_bslash(self):
        self.assertEqual(views._sieve_quote("fo\\o"), '"fo\\\\o"')

    def test_sieve_quote_dquotes(self):
        self.assertEqual(views._sieve_quote('fo"o'), '"fo\\"o"')

    def test_sieve_quote_multi_dquotes(self):
        self.assertEqual(views._sieve_quote('fo"""""o'),
                         '"fo\\"\\"\\"\\"\\"o"')

    def test_sieve_quote_combo(self):
        self.assertEqual(views._sieve_quote('f\'\'\\\\o\'\\"\\"o'),
                         '"f\'\'\\\\\\\\o\'\\\\\\"\\\\\\"o"')

    def test_sieve_quote_unicode(self):
        self.assertEqual(views._sieve_quote(u'\u2603\\"'),
                         u'"\u2603\\\\\\""')


class TestMakeScript(unittest.TestCase):

    def test_make_script(self):
        email_address = u'nobody@isotomadev.com'
        subject = u'My subject'
        message = u'Go away'
        days = 1
        template = u'{email}\n{subject}\n{contents}\n{days}'
        script = views._make_script(email_address,
                                    subject,
                                    message,
                                    days,
                                    template=template)
        self.assertEqual(script.split(u'\n'),
                         [u'"nobody@isotomadev.com"',
                          u'"My subject"',
                          u'"Go away"',
                          u'1'])

    def test_make_script_escapes(self):
        email_address = u'"no\\"body"@isotomadev.com'
        subject = u'"My \\"subject\\""'
        message = u'"Go away"'
        days = 1
        template = u'{email}\n{subject}\n{contents}\n{days}'
        script = views._make_script(email_address,
                                    subject,
                                    message,
                                    days,
                                    template=template)
        self.assertEqual(script.split(u'\n'),
                         [u'"\\"no\\\\\\"body\\"@isotomadev.com"',
                          u'"\\"My \\\\\\"subject\\\\\\"\\""',
                          u'"\\"Go away\\""',
                          u'1'])

    def test_make_script_unicode(self):
        email_address = u'nob\u2603dy@isotomadev.com'
        subject = u'My subject \u2603'
        message = u'Go away \u2603'
        days = 1
        template = u'{email}\n{subject}\n{contents}\n{days}'
        script = views._make_script(email_address,
                                    subject,
                                    message,
                                    days,
                                    template=template)
        self.assertEqual(script.split(u'\n'),
                         [u'"nob\u2603dy@isotomadev.com"',
                          u'"My subject \u2603"',
                          u'"Go away \u2603"',
                          u'1'])


class TestSetAwayMessageScript(unittest.TestCase):

    def setUp(self):
        self.client = mock.Mock()
        self.have_space = True
        havespace = lambda name, size, self=self: self.have_space
        self.client.havespace.side_effect = havespace
        self.parser_cls = mock.Mock()
        self.parser = self.parser_cls.return_value
        self.parse_success = True
        parse = lambda x, self=self: self.parse_success
        self.parser.parse.side_effect = parse

    def test_set_away_message_script(self):
        views._write_and_activate_script(self.client, u'foo',
                                         parser_cls=self.parser_cls)
        self.assertEqual(self.parser.parse.call_count, 1)
        self.assertEqual(self.parser.parse.call_args, ((u'foo',), {}))
        self.assertEqual(self.client.havespace.call_args,
                         ((views.SCRIPT_NAME, 3), {}))
        self.assertEqual(self.client.putscript.call_args,
                         ((views.SCRIPT_NAME, u'foo'), {}))
        self.assertEqual(self.client.setactive.call_args,
                         ((views.SCRIPT_NAME,), {}))

    def test_set_away_message_script_parsing_failed(self):
        self.parse_success = False
        self.assertRaises(AssertionError,
                          views._write_and_activate_script,
                          self.client, u'foo',
                          parser_cls=self.parser_cls
                          )
        self.assertEqual(self.parser.parse.call_count, 1)
        self.assertEqual(self.parser.parse.call_args, ((u'foo',), {}))
        self.assertEqual(self.client.havespace.call_count, 0)
        self.assertEqual(self.client.putscript.call_count, 0)
        self.assertEqual(self.client.setactive.call_count, 0)

    def test_set_away_message_script_no_space(self):
        self.have_space = False
        self.assertRaises(RuntimeError,
                          views._write_and_activate_script,
                          self.client, u'foo',
                          parser_cls=self.parser_cls
                          )
        self.assertEqual(self.parser.parse.call_count, 1)
        self.assertEqual(self.parser.parse.call_args, ((u'foo',), {}))
        self.assertEqual(self.client.havespace.call_args,
                         ((views.SCRIPT_NAME, 3), {}))
        self.assertEqual(self.client.putscript.call_count, 0)
        self.assertEqual(self.client.setactive.call_count, 0)


class TestValidateSieveCredentials(unittest.TestCase):

    def setUp(self):
        self.client_cls = mock.Mock()
        self.client = self.client_cls.return_value

        def connect(username, password):
            if password != 'password':
                raise views.sievelib.managesieve.Error('Error')

        self.client.connect.side_effect = connect

    def test_validate_sieve_credentials(self):
        result = views._validate_sieve_credentials(u'nobody', u'password',
                                                  client_cls=self.client_cls)
        self.assertEquals(result, None)

    def test_validate_sieve_credentials_bad_credentials(self):
        self.client.connect.side_effect
        result = views._validate_sieve_credentials(u'nobody', u'bad password',
                                                  client_cls=self.client_cls)
        self.assertNotEquals(result, None)
        self.assertEquals(str(result), 'Error')


class TestIndexView(unittest.TestCase):

    def _validate(self, username, password):
        if password != u'password':
            return views.sievelib.managesieve.Error('Error')
        return None

    def setUp(self):
        self.render = mock.Mock()
        self.request = mock.Mock()
        self.request.method = 'GET'
        self.request.POST = {}
        self.request.session = {}
        self.form_cls = mock.Mock()
        self.form = self.form_cls.return_value
        self.form_data = {}
        self.form.cleaned_data = self.form_data
        self.valid_form = True
        self.validate = mock.Mock()
        self.validate.side_effect = self._validate
        valid_form = lambda self=self: self.valid_form
        self.form.is_valid.side_effect = valid_form

    def test_index(self):
        result = views.index(self.request, self.form_cls, self.render,
                             self.validate)
        self.assertEqual(result, self.render.return_value)
        self.assertEqual(self.render.call_count, 1)
        self.assertEqual(self.form_cls.call_count, 1)
        self.assertEqual(self.form_cls.call_args, ((), {}))
        self.assertEqual(self.render.call_args,
                         ((self.request, views.INDEX_TEMPLATE, {
                            'login': self.form,
                            'error_message': None,
                           }), {}))

    def test_index_post(self):
        self.request.method = 'POST'
        self.request.POST = {
            'email': u'nobody@isotomadev.com',
            'username': u'nobody',
            'password': u'password',
            }
        self.form_data.update(self.request.POST)
        self.assertEqual(self.request.session, {})
        result = views.index(self.request, self.form_cls, self.render,
                             self.validate)
        self.assertTrue(isinstance(result, views.HttpResponseRedirect))
        self.assertEqual(result['Location'], 'message')
        self.assertEqual(self.render.call_count, 0)
        self.assertEqual(self.form_cls.call_args[0], (self.request.POST,))
        self.assertEqual(self.form.is_valid.call_count, 1)
        self.assertEqual(self.validate.call_count, 1)
        self.assertEqual(self.validate.call_args,
                         ((u'nobody', u'password'), {}))
        self.assertEqual(self.request.session,
                         {'authenticated': True,
                          'username': u'nobody',
                          'password': u'password',
                          'email': u'nobody@isotomadev.com',
                          })

    def test_index_post_invalid_form(self):
        self.request.method = 'POST'
        self.valid_form = False
        self.request.POST = {
            'email': u'nobody@isotomadev.com',
            'username': u'nobody',
            'password': u'password',
            }
        self.form_data.update(self.request.POST)
        self.assertEqual(self.request.session, {})
        result = views.index(self.request, self.form_cls, self.render,
                             self.validate)
        self.assertEqual(self.form_cls.call_args[0], (self.request.POST,))
        self.assertEqual(self.form.is_valid.call_count, 1)
        self.assertEqual(self.validate.call_count, 0)
        self.assertEqual(self.request.session, {})
        self.assertEqual(result, self.render.return_value)
        self.assertEqual(self.render.call_count, 1)
        self.assertEqual(self.render.call_args,
                         ((self.request, views.INDEX_TEMPLATE, {
                            'login': self.form,
                            'error_message': None,
                           }), {}))

    def test_index_post_invalid_credentials(self):
        self.request.method = 'POST'
        self.request.POST = {
            'email': u'nobody@isotomadev.com',
            'username': u'nobody',
            'password': u'drowssap',
            }
        self.form_data.update(self.request.POST)
        self.assertEqual(self.request.session, {})
        result = views.index(self.request, self.form_cls, self.render,
                             self.validate)
        self.assertEqual(self.form_cls.call_args[0], (self.request.POST,))
        self.assertEqual(self.form.is_valid.call_count, 1)
        self.assertEqual(self.validate.call_count, 1)
        self.assertEqual(self.validate.call_args,
                         ((u'nobody', u'drowssap'), {}))
        self.assertEqual(self.request.session,
                         {'username': u'nobody',
                          'password': u'drowssap',
                          'email': u'nobody@isotomadev.com',
                          'authenticated': False,
                          })
        self.assertEqual(result, self.render.return_value)
        self.assertEqual(self.render.call_count, 1)
        self.assertEqual(self.render.call_args[0][:2],
                         (self.request, views.INDEX_TEMPLATE))
        self.assertEqual(self.render.call_args[0][2]['login'], self.form)
        self.assertEqual(str(self.render.call_args[0][2]['error_message']),
                         'Error')


class TestActivate(unittest.TestCase):

    def setUp(self):
        self.request = mock.Mock()
        self.request.session = {
            'email': u'nobody@isotomadev.com',
            }
        self.client = mock.Mock()
        self.form_cls = mock.Mock()
        self.form = self.form_cls.return_value
        self.form.cleaned_data = {
            'subject': u'Test subject',
            'message': u'Message',
            'days': 3,
            }
        self.form.is_valid.return_value = True
        self.make_script = mock.Mock()
        self.make_script.return_value = u'scriptyscript'
        self.set_script = mock.Mock()

    def test_activate(self):
        result = views._activate(self.request, self.client, self.form_cls,
                                 self.make_script, self.set_script)
        self.assertEqual(result, self.form)
        self.assertEqual(self.make_script.call_args,
                         ((u'nobody@isotomadev.com', u'Test subject',
                           u'Message', 3),
                          {})
                         )
        self.assertEqual(self.set_script.call_args,
                         ((self.client, u'scriptyscript'), {}))

    def test_activate_invalid_form(self):
        self.form.is_valid.return_value = False
        result = views._activate(self.request, self.client, self.form_cls,
                                 self.make_script, self.set_script)
        self.assertEqual(result, self.form)
        self.assertEqual(self.make_script.call_count, 0)
        self.assertEqual(self.set_script.call_count, 0)


class TestIsHolidayScriptActive(unittest.TestCase):

    def setUp(self):
        self.client = mock.Mock()
        self.active_script = views.SCRIPT_NAME
        self.other_scripts = []
        listscripts = lambda self=self: (self.active_script,
                                         self.other_scripts)
        self.client.listscripts.side_effect = listscripts

    def test_is_holiday_script_active(self):
        result = views._is_holiday_script_active(self.client)
        self.assertTrue(result)
        self.assertEqual(self.client.listscripts.call_count, 1)
        self.assertEqual(self.client.setactive.call_count, 0)

    def test_is_holiday_script_active_not_active(self):
        self.active_script = u''.join(views.SCRIPT_NAME[::-1])
        result = views._is_holiday_script_active(self.client)
        self.failIf(result)
        self.assertEqual(self.client.listscripts.call_count, 1)
        self.assertEqual(self.client.setactive.call_count, 0)

    def test_is_holiday_script_active_ingo_active(self):
        self.active_script = u'ingo'
        result = views._is_holiday_script_active(self.client)
        self.failIf(result)
        self.assertEqual(self.client.listscripts.call_count, 1)
        self.assertEqual(self.client.setactive.call_count, 1)
        self.assertEqual(self.client.setactive.call_args, ((u'',), {}))
