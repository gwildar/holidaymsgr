#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
sieve.py - v0.1.0 - 2006.08.01

Author : Alexandre Norman - norman@xael.org
Licence : GPL

"""

############################################################################

class SieveError(Exception):
    pass
    
############################################################################

import socket
import types
import string

############################################################################




class sieve:

    def __init__(self, server, port=2000):
        """
        server : string, server name or address
        port : int sieve port
        """

        # Socket stream to the server
        s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.connect((server, port))
        except socket.error:
            raise Exception('Could not reach sieve using network (%s, %s)' % (server, port))

        self.socket = s

        # Do nothing with it :-/
        banner = self.__get__()
        return


    def authenticate(self, login, passwd):
        """
        login : string
        passwd : string
        """
        # Encode authentication scheme
        auth = (chr(0)+login+chr(0)+passwd).encode("base64")
        s = ('AUTHENTICATE "PLAIN" "%s"' % auth).replace('\n','')
        # Send it...
        self.__send__(s)
        rep = self.__get__()
        # Is it ok ?
        if rep[:2] == 'NO':
            raise SieveError(rep)
        
        return

    def putscript(self, scriptname, script):
        """
        scriptname : string
        script : string
        """
        lenght = len(script)

        # upload the script
        st = 'PUTSCRIPT "%s" {%s+}\r\n%s\n' % (scriptname, lenght, script)

        self.__send__(st)
        data = self.__get__()
        # Ok ?
        if data[:2] == 'NO':
            raise Exception(data)       
        return


    def listscripts(self):
        """
        return a list of scripts
        """
        self.__send__('LISTSCRIPTS')
        rep = self.__get__()

        scripts = []
        for line in rep.split('\n'):
            try:
                scripts.append(line.split('"')[1])
            except:
                pass            
        return scripts


    def get_active(self):
        """
        Get the name of the active script
        """
        self.__send__('LISTSCRIPTS')
        rep = self.__get__()
        for line in rep.split('\n'):
            if line[-7:-1]=='ACTIVE':
                try:
                    return line.split('"')[1]
                except:
                    pass            
        return None
        


    def getscript(self, scriptname):
        """
        scriptname : string

        return script named scriptname
        """
        self.__send__('GETSCRIPT "%s"' % scriptname)
        data = self.__get__()
        if data[:2] == 'NO':
            raise Exception(data)
        # Get message lenght
        nb = int(data.split('\n')[0][1:-2])
        first = len(data.split('\n')[0])
        return data[first+1:first+nb]


    def activate(self, scriptname):
        """
        scriptname : string

        active string named scriptname
        """
        self.__send__('SETACTIVE "%s"' % scriptname)
        data = self.__get__()
        if data[:2] == 'NO':
            raise Exception(data)       
        return


    def desactivate(self):
        """
        desactivate all scripts
        """
        self.activate('')
        return


    def __send__(self, data):
        """
        internal : send data
        """
        self.socket.send(data+'\n')
        return

    def __get__(self):
        """
        internal : get data
        """
        data = self.socket.recv(20000)
        return data

# MAIN -------------------
if __name__ == '__main__':

    # init sieve object
    s = sieve('127.0.0.1')

    # Authenticate
    s.authenticate('alexandre.norman','XXXXXX')

    # get scripts on server
    l = s.listscripts()
    print l

    # upload a script
    s.putscript('tortuegenial',"""
    # Set by vacation.py v0.1.0 [A.Norman]
    require "vacation";
    vacation :addresses ["alexandre.norman@mnh.fr"]
    "Absent, retour lundi 3/07/06
    ";

    redirect "alexandre.norman@mnh.fr";
    keep;
    """)

    # activate it
    s.activate('tortuegenial')

    # get active script -> tortuegenial
    print s.get_active()

    # desactivate 
    s.desactivate()

    # get active script -> none
    print s.get_active()


