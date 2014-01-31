#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
This plugin activate checkbox to disable /manager for domain

Author: Andrey Scopenco <andrey@scopenco.net>
'''

PLUGIN_NAME = 'ispmgr_off'
LOG_FILE = '/usr/local/ispmgr/var/ispmgr.log'

from xml.dom import minidom
from os import chdir, getpid, environ, access, R_OK, chown, listdir
from sys import exit, stderr
from cgi import FieldStorage
from traceback import format_exc


class ExitOk(Exception):
    pass


class Log(object):
    '''Class used for add debug to ispmgr.log'''
    def __init__(self, plugin=None, output=LOG_FILE):
        import time
        timenow = time.localtime(time.time())
        self.timef = time.strftime("%b %d %H:%M:%S", timenow)
        self.log = output
        self.plugin_name = plugin
        self.fsock = open(self.log, 'a+')
        self.pid = getpid()
        self.script_name = __file__

    def write(self, desc):
        if not (desc == "\n"):
            if (desc[-1:] == "\n"):
                self.fsock.write(
                    '%s [%s] ./%s \033[36;40mPLUGIN %s :: %s\033[0m' % (
                        self.timef, self.pid, self.script_name,
                        self.plugin_name, desc))
            else:
                self.fsock.write(
                    '%s [%s] ./%s \033[36;40mPLUGIN %s :: %s\033[0m\n' % (
                        self.timef, self.pid, self.script_name,
                        self.plugin_name, desc))

    def close(self):
        self.fsock.close()


def xml_doc(elem=None, text=None):
    xmldoc = minidom.Document()
    doc = xmldoc.createElement('doc')
    xmldoc.appendChild(doc)
    if elem:
        emp = xmldoc.createElement(elem)
        doc.appendChild(emp)
        if text:
            msg_text = xmldoc.createTextNode(text)
            emp.appendChild(msg_text)
    return xmldoc.toxml('UTF-8')


def xml_error(text, code_num=None):
    xmldoc = minidom.Document()
    doc = xmldoc.createElement('doc')
    xmldoc.appendChild(doc)
    error = xmldoc.createElement('error')
    doc.appendChild(error)
    if code_num:
        code = xmldoc.createAttribute('code')
        error.setAttributeNode(code)
        error.setAttribute('code', str(code_num))
        if code_num in [2, 3, 6]:
            obj = xmldoc.createAttribute('obj')
            error.setAttributeNode(obj)
            error.setAttribute('obj', str(text))
            return xmldoc.toxml('UTF-8')
        elif code_num in [4, 5]:
            val = xmldoc.createAttribute('val')
            error.setAttributeNode(val)
            error.setAttribute('val', str(text))
            return xmldoc.toxml('UTF-8')
    error_text = xmldoc.createTextNode(text.decode('utf-8'))
    error.appendChild(error_text)
    return xmldoc.toxml('UTF-8')

if __name__ == "__main__":
    chdir('/usr/local/ispmgr/')

    # activate logging
    # stderr ==> ispmgr.log
    log = Log(plugin=PLUGIN_NAME)
    stderr = log

    try:
        # get cgi vars
        req = FieldStorage(keep_blank_values=True)
        func = req.getvalue('func')
        elid = req.getvalue('elid')
        sok = req.getvalue('sok')

        log.write('func %s, elid %s, sok %s' % (func, elid, sok))

        if func != 'wwwdomain.edit' or elid or sok:
            print xml_doc()
            raise ExitOk('no action')

        print xml_doc('switchispmgr', 'on')
        raise ExitOk('done')

    except ExitOk, e:
        log.write(e)
    except:
        print xml_error('please contact support team', code_num='1')
        log.write(format_exc())
        exit(0)
