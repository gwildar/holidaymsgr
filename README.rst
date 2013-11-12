=================
Holiday Messenger
=================

A Django application for managing vacation messages for Cyrus.

The application provides a small web application that allows you to set or
unset vacation message handling, and change your vacation message.

The application communicates with Cyrus (and potentially other mail systems)
using Sieve (RFC5228) scripts and a ManageSieve (RFC5804) client.

Installation
============

$ virtualenv /var/local/sites/<sitename>
$ source /var/local/sites/<sitename>/bin/activate

Features
========

When you visit the site you will be asked for:

 * your email address
 * your username
 * your password

Your email address is required because Cyrus itself doesn't know which
addresses you receive mail at.

The username and password should be your login credentials for Cyrus (these are
what you put into your IMAP mail client).

Once you have logged in, if your vacation message is not active you will be presented with a form asking for the subject and contents of your vacation message. You can then save and activate your message.

If your vacation message is active, you will also have an option to deactivate
it.


Vacation processing
===================

When vacation mode is enabled, every inbound email is inspected. If the email
fits the criteria below then it is delivered as usual, but in addition an
autoresponse is generated informing the sender that the recipient is on
vacation.

The message generated will contain the subject and message set by the user of
the web application.

Vacation criteria
=================

 1. The message does not have one of the following headers, that are considered signs that the message is automated:

  * list-help
  * list-unsubscribe
  * list-subscribe
  * list-owner
  * list-post
  * list-archive
  * list-id
  * Mailing-List

 2. The message does not have a Precedence header with one of the values:

  * bulk
  * list
  * junk

 3. The To header does not begin "Multiple recipients of"

 4. The sender has not previously been sent an automated vacation message by this system for this recipient in the previous 14 days

The intention is that a human email sender will not be "spammed" with vacation
messages, but will instead receive a response for each vacationer a maximum of
once every 14 days.


