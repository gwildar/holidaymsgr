# $Id$
# encoding: utf-8
"""holidaymsgr.holidays.forms"""
__author__ = 'Richard Mitchell <richard.mitchell@isotoma.com>'
__docformat__ = 'restructuredtext en'
__version__ = '$Revision$'[11:-2]

from django import forms


class MailForm(forms.Form):

    subject = forms.CharField()
    message = forms.CharField(widget=forms.Textarea)
    days = forms.IntegerField(min_value=1)
    subject.widget.attrs = {'class': 'form-control'}
    message.widget.attrs = {'class': 'form-control'}
    days.widget.attrs = {'class': 'form-control'}


class LoginForm(forms.Form):

    email = forms.EmailField(label="Email Address")
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
    email.widget.attrs = {'class': 'form-control'}
    username.widget.attrs = {'class': 'form-control'}
    password.widget.attrs = {'class': 'form-control'}
