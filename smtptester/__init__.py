from __future__ import absolute_import

import getpass
import os
import random
import re
import smtplib
import socket
import string
import sys
import traceback
import thread
import time

import dns.resolver
import wx
import wx.lib.delayedresult as delayedresult
from wx.lib.wordwrap import wordwrap

from . import util
from . import validators


__app_name__ = 'SMTP Tester'
__version_info__ = ('0', '1', '5')
__version__ = '.'.join(__version_info__)
__author__ = 'Michael Paul Thomas Conigliaro'
__author_email__ = 'mike [at] conigliaro [dot] org'
__artist__ = 'Mark James (Silk icons from famfamfam.com)'
__copyright__ = "(c) %s %s" % (time.strftime('%Y'), __author__)
__url__ = 'http://github.com/mconigliaro/%s' % ''.join(__app_name__.lower().split())
__description__ = 'A cross-platform graphical SMTP diagnostic tool'


if hasattr(sys, 'frozen'):
    import win32api
    APP_ICON = win32api.GetModuleFileName(win32api.GetModuleHandle(None))
else:
    APP_ICON = os.path.normpath(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'data', 'smtptester.xpm'))

APP_CONFIG = 'smtptester'
APP_DEFAULT_WIDTH = 525
APP_DEFAULT_HEIGHT = 700

ERROR = '#cc0000'
WARNING = '#ff6633'
INFO = '#999999'
ACTION = '#0000ff'
RESULT = '#009900'
NOTSET = '#000000'

SMTP_DEFAULT_PORT = 25
SMTP_DEFAULT_CONNECT_TIMEOUT = 10
SMTP_DEBUGLEVEL = 0
DNS_DEFAULT_PORT = 53
DNS_DEFAULT_QUERY_TIMEOUT = 10


class SmtpTester(wx.Frame):

    def __init__(self, parent, id, title):
        # Set config file
        self.cfg = wx.Config(APP_CONFIG)

        # Initialize frame/panel
        wx.Frame.__init__(self, parent, id, title,
          size=(self.cfg.ReadInt('appWidth', APP_DEFAULT_WIDTH),
                self.cfg.ReadInt('appHeight', APP_DEFAULT_HEIGHT)))
        self.SetIcon(wx.Icon(APP_ICON, wx.BITMAP_TYPE_ANY))
        self.panel = wx.Panel(self)

        # Define file menu
        fileMenu = wx.Menu()
        fileExitMenuItem = fileMenu.Append(wx.ID_ANY,
            'E&xit', 'Terminate the program')

        # Define options menu
        optionsMenu = wx.Menu()
        self.saveSettingsMenuItem = optionsMenu.Append(wx.ID_ANY,
            'S&ave Settings on Exit', 'Save Settings on Exit', wx.ITEM_CHECK)
        self.saveSettingsMenuItem.Check()

        # Define help menu
        helpMenu = wx.Menu()
        helpAboutMenuItem = helpMenu.Append(wx.ID_ANY,
            '&About', 'Information about this program')

        # Assign menus to menu bar
        menuBar = wx.MenuBar()
        menuBar.Append(fileMenu,'&File')
        menuBar.Append(optionsMenu,'&Options')
        menuBar.Append(helpMenu,'&Help')
        self.SetMenuBar(menuBar)

        # Initialize thread variables
        self.jobID = 0
        self.abortEvent = delayedresult.AbortEvent()

        # Define controls
        self.mailFromTextCtrl = wx.TextCtrl(self.panel, value=self.cfg.Read('mailFrom', self.getMyEmailAddress()), validator=validators.EmailAddressValidator())
        self.mailToTextCtrl = wx.TextCtrl(self.panel, value=self.cfg.Read('mailTo'), validator=validators.EmailAddressValidator())
        self.mailToTextCtrl.SetFocus()
        self.mailMsgTextCtrl = wx.TextCtrl(self.panel, style=wx.TE_MULTILINE,
            value="X-Mailer: %s %s\nFrom: %s\nTo: %s\nSubject: Test message\n\nThis is a test." %
                (__app_name__, __version__, self.cfg.Read('mailFrom', self.getMyEmailAddress()), self.cfg.Read('mailTo')))
        self.useNsCheckBox = wx.CheckBox(self.panel, label='Specify DNS server')
        self.useNsCheckBox.SetValue(self.cfg.ReadBool('useNs'))
        self.useNsHostTextCtrl = wx.TextCtrl(self.panel, value=self.cfg.Read('useNsHost'), validator=validators.HostAddressValidator())
        self.useNsPortSpinCtrl = wx.SpinCtrl(self.panel, value=self.cfg.Read('useNsPort', str(DNS_DEFAULT_PORT)), min=1, max=65535, size=(50,-1))
        self.nsQueryTimeoutSpinCtrl = wx.SpinCtrl(self.panel, value=self.cfg.Read('nsQueryTimeout', str(DNS_DEFAULT_QUERY_TIMEOUT)), min=1, max=65535, size=(50,-1))
        self.useNsTcpCheckBox = wx.CheckBox(self.panel, label='Use TCP')
        self.useNsTcpCheckBox.SetValue(self.cfg.ReadBool('useNsTcp'))
        self.useSmtpCheckBox = wx.CheckBox(self.panel, label='Specify SMTP server')
        self.useSmtpCheckBox.SetValue(self.cfg.ReadBool('useSmtp'))
        self.useSmtpHostTextCtrl = wx.TextCtrl(self.panel, value=self.cfg.Read('useSmtpHost'), validator=validators.HostAddressValidator())
        self.useSmtpPortSpinCtrl = wx.SpinCtrl(self.panel, value=self.cfg.Read('useSmtpPort', str(SMTP_DEFAULT_PORT)), min=1, max=65535, size=(50,-1))
        self.smtpConnectTimeoutSpinCtrl = wx.SpinCtrl(self.panel, value=self.cfg.Read('smtpConnectTimeout', str(SMTP_DEFAULT_CONNECT_TIMEOUT)), min=1, max=65535, size=(50,-1))
        self.useSmtpHeloTextCtrl = wx.TextCtrl(self.panel, value=self.cfg.Read('useSmtpHelo', socket.getfqdn()), validator=validators.HostAddressValidator())
        self.useAuthCheckBox = wx.CheckBox(self.panel, label='Use Authentication')
        self.useAuthCheckBox.SetValue(self.cfg.ReadBool('useAuth'))
        self.useAuthUserTextCtrl = wx.TextCtrl(self.panel, value=self.cfg.Read('useAuthUser'), validator=validators.GenericTextValidator(flag=validators.VALIDATE_NOT_NULL))
        self.useAuthPassTextCtrl = wx.TextCtrl(self.panel, value=self.cfg.Read('useAuthPass'), style=wx.TE_PASSWORD)
        self.useTlsCheckBox = wx.CheckBox(self.panel, label='Use TLS encryption')
        self.useTlsCheckBox.SetValue(self.cfg.ReadBool('useTls'))
        self.okButton = wx.Button(self.panel, wx.ID_OK)
        self.cancelButton = wx.Button(self.panel, wx.ID_CANCEL)
        self.resultsTextCtrl = wx.TextCtrl(self.panel, style=wx.TE_MULTILINE|wx.TE_RICH2|wx.TE_READONLY)

        # Put all controls into correct state
        if not self.useNsCheckBox.IsChecked():
            self.toggleNsOptions(False)
        if not self.useSmtpCheckBox.IsChecked():
            self.toggleSmtpOptions(False)
        if not self.useAuthCheckBox.IsChecked():
            self.toggleAuthOptions(False)
        self.toggleWorkingMode(False)

        # Outer sizer (entire window)
        mainSizer = wx.GridBagSizer(vgap=5, hgap=5)

        # Message fields
        messageSizer = wx.StaticBoxSizer(wx.StaticBox(self.panel, label='Message'), orient=wx.VERTICAL)
        messageSizer.Add(wx.StaticText(self.panel, label='From:'))
        messageSizer.Add(self.mailFromTextCtrl, flag=wx.ALL|wx.EXPAND)
        messageSizer.Add(wx.StaticText(self.panel, label='To:'))
        messageSizer.Add(self.mailToTextCtrl, flag=wx.ALL|wx.EXPAND)
        messageSizer.Add(wx.StaticText(self.panel, label='Message:'))
        messageSizer.Add(self.mailMsgTextCtrl, proportion=1, flag=wx.ALL|wx.EXPAND)
        mainSizer.Add(messageSizer, pos=(0,0), span=(4,1), flag=wx.ALL|wx.EXPAND)

        # DNS Options
        nsSizer = wx.StaticBoxSizer(wx.StaticBox(self.panel, label='DNS'), orient=wx.VERTICAL)
        innerSizer = wx.GridBagSizer()
        innerSizer.SetEmptyCellSize((0,0)) # FIXME http://trac.wxwidgets.org/ticket/3105
        innerSizer.Add(self.useNsCheckBox, pos=(3,0), span=(1,2))
        innerSizer.Add(wx.StaticText(self.panel, label='Host:'), pos=(4,0))
        innerSizer.Add(self.useNsHostTextCtrl, pos=(5,0), flag=wx.ALL|wx.EXPAND)
        innerSizer.Add(wx.StaticText(self.panel, label='Port:'), pos=(4,1))
        innerSizer.Add(self.useNsPortSpinCtrl, pos=(5,1))
        innerSizer.Add(wx.StaticText(self.panel, label='Timeout:'), pos=(4,2))
        innerSizer.Add(self.nsQueryTimeoutSpinCtrl, pos=(5,2), flag=wx.ALL|wx.EXPAND)
        innerSizer.Add(self.useNsTcpCheckBox, pos=(6,0), span=(1,2))
        nsSizer.Add(innerSizer, flag=wx.ALL|wx.EXPAND)
        mainSizer.Add(nsSizer, pos=(0,1), flag=wx.ALL|wx.EXPAND)

        # SMTP Server Options
        smtpSizer = wx.StaticBoxSizer(wx.StaticBox(self.panel, label='SMTP'), orient=wx.VERTICAL)
        innerSizer = wx.GridBagSizer()
        innerSizer.SetEmptyCellSize((0,0)) # FIXME http://trac.wxwidgets.org/ticket/3105
        innerSizer.Add(self.useSmtpCheckBox, pos=(3,0), span=(1,2))
        innerSizer.Add(wx.StaticText(self.panel, label='Host:'), pos=(4,0))
        innerSizer.Add(self.useSmtpHostTextCtrl, pos=(5,0), flag=wx.ALL|wx.EXPAND)
        innerSizer.Add(wx.StaticText(self.panel, label='Port:'), pos=(4,1))
        innerSizer.Add(self.useSmtpPortSpinCtrl, pos=(5,1))

        innerSizer.Add(wx.StaticText(self.panel, label='Timeout:'), pos=(4,2))
        innerSizer.Add(self.smtpConnectTimeoutSpinCtrl, pos=(5,2), flag=wx.ALL|wx.EXPAND)

        innerSizer.Add(wx.StaticText(self.panel, label='HELO/EHLO:'), pos=(6,0))
        innerSizer.Add(self.useSmtpHeloTextCtrl, pos=(7,0), span=(1,3), flag=wx.ALL|wx.EXPAND)
        smtpSizer.Add(innerSizer, flag=wx.ALL|wx.EXPAND)
        mainSizer.Add(smtpSizer, pos=(1,1), flag=wx.ALL|wx.EXPAND)

        # Security Options
        secSizer = wx.StaticBoxSizer(wx.StaticBox(self.panel, label='Security'), orient=wx.VERTICAL)
        secSizer.Add(self.useAuthCheckBox)
        secSizer.Add(wx.StaticText(self.panel, label='Username:'))
        secSizer.Add(self.useAuthUserTextCtrl, flag=wx.ALL|wx.EXPAND)
        secSizer.Add(wx.StaticText(self.panel, label='Password:'))
        secSizer.Add(self.useAuthPassTextCtrl, flag=wx.ALL|wx.EXPAND)
        secSizer.Add(self.useTlsCheckBox)
        mainSizer.Add(secSizer, pos=(2,1), flag=wx.ALL|wx.EXPAND)

        # Buttons
        buttonSizer = wx.StdDialogButtonSizer()
        buttonSizer.AddButton(self.okButton)
        buttonSizer.AddButton(self.cancelButton)
        buttonSizer.Realize()
        mainSizer.Add(buttonSizer, pos=(3,1), flag=wx.ALIGN_BOTTOM|wx.ALIGN_CENTER_HORIZONTAL)

        # Results window
        resultsSizer = wx.StaticBoxSizer(wx.StaticBox(self.panel, label='Results'), orient=wx.VERTICAL)
        resultsSizer.Add(self.resultsTextCtrl, proportion=1, flag=wx.ALL|wx.EXPAND)
        mainSizer.Add(resultsSizer, pos=(4,0), span=(1,2), flag=wx.ALL|wx.EXPAND)

        # End outer sizer (entire window)
        mainSizer.AddGrowableCol(0)
        mainSizer.AddGrowableRow(4)
        self.panel.SetSizerAndFit(mainSizer)
        self.panel.SetClientSize(mainSizer.GetSize())
        self.Show()

        # Map events
        self.Bind(wx.EVT_MENU, self.onFileExit, fileExitMenuItem)
        self.Bind(wx.EVT_MENU, self.onHelpAbout, helpAboutMenuItem)
        self.Bind(wx.EVT_CLOSE, self.onCloseWindow)
        self.mailFromTextCtrl.Bind(wx.EVT_TEXT, self.onUpdateMailFromTextCtrl)
        self.mailToTextCtrl.Bind(wx.EVT_TEXT, self.onUpdateMailToTextCtrl)
        self.useNsCheckBox.Bind(wx.EVT_CHECKBOX, self.onUseNsCheckBox)
        self.useSmtpCheckBox.Bind(wx.EVT_CHECKBOX, self.onUseSmtpCheckBox)
        self.useAuthCheckBox.Bind(wx.EVT_CHECKBOX, self.onAuthCheckBox)
        self.cancelButton.Bind(wx.EVT_BUTTON, self.onCancel)
        self.okButton.Bind(wx.EVT_BUTTON, self.onOk)

    def onFileExit(self, e):
        self.Close(True)

    def onCloseWindow(self, e):
        if self.saveSettingsMenuItem.IsChecked():
            self.cfg.WriteInt('appWidth', self.GetSizeTuple()[0])
            self.cfg.WriteInt('appHeight', self.GetSizeTuple()[1])
            self.cfg.Write('mailFrom', self.mailFromTextCtrl.GetValue())
            self.cfg.Write('mailTo', self.mailToTextCtrl.GetValue())
            self.cfg.WriteBool('useNs', self.useNsCheckBox.GetValue())
            self.cfg.Write('useNsHost', self.useNsHostTextCtrl.GetValue())
            self.cfg.Write('useNsPort', str(self.useNsPortSpinCtrl.GetValue()))
            self.cfg.Write('nsQueryTimeout', str(self.nsQueryTimeoutSpinCtrl.GetValue()))
            self.cfg.WriteBool('useNsTcp', self.useNsTcpCheckBox.GetValue())
            self.cfg.WriteBool('useSmtp', self.useSmtpCheckBox.GetValue())
            self.cfg.Write('useSmtpHost', self.useSmtpHostTextCtrl.GetValue())
            self.cfg.Write('useSmtpPort', str(self.useSmtpPortSpinCtrl.GetValue()))
            self.cfg.Write('smtpConnectTimeout', str(self.smtpConnectTimeoutSpinCtrl.GetValue()))
            self.cfg.Write('useSmtpHelo', self.useSmtpHeloTextCtrl.GetValue())
            self.cfg.WriteBool('useAuth', self.useAuthCheckBox.GetValue())
            self.cfg.Write('useAuthUser', self.useAuthUserTextCtrl.GetValue())
            self.cfg.Write('useAuthPass', self.useAuthPassTextCtrl.GetValue())
            self.cfg.WriteBool('useTls', self.useTlsCheckBox.GetValue())
        else:
            self.cfg.DeleteAll()
        self.Destroy()

    def onHelpAbout(self, e):
        info = wx.AboutDialogInfo()
        info.Name = __app_name__
        info.Version = __version__
        info.Copyright = __copyright__
        info.Description = __description__
        info.WebSite = (__url__, __url__)
        info.Developers = ['%s <%s>' % (__author__, __author_email__)]
        info.Artists = [__artist__]
        wx.AboutBox(info)

    def toggleWorkingMode(self, value):
        if value:
            self.okButton.Enable(False)
            self.cancelButton.Enable(True)
        else:
            self.okButton.Enable(True)
            self.cancelButton.Enable(False)

    def onUpdateMailFromTextCtrl(self, e):
        mailFrom = self.mailFromTextCtrl.GetValue()
        mailMsg = self.mailMsgTextCtrl.GetValue()
        c_pattern_mail_to = re.compile('From:.*')
        self.mailMsgTextCtrl.SetValue(c_pattern_mail_to.sub("From: %s" % mailFrom, mailMsg))

    def onUpdateMailToTextCtrl(self, e):
        mailTo = self.mailToTextCtrl.GetValue()
        mailMsg = self.mailMsgTextCtrl.GetValue()
        c_pattern_mail_to = re.compile('To:.*')
        self.mailMsgTextCtrl.SetValue(c_pattern_mail_to.sub("To: %s" % mailTo, mailMsg))

    def onUseNsCheckBox(self, e):
        self.toggleNsOptions(e.IsChecked())

    def onUseSmtpCheckBox(self, e):
        self.toggleSmtpOptions(e.IsChecked())

    def onAuthCheckBox(self, e):
        self.toggleAuthOptions(e.IsChecked())

    def toggleNsOptions(self, value):
        self.useNsHostTextCtrl.Enable(value)
        self.useNsPortSpinCtrl.Enable(value)

    def toggleSmtpOptions(self, value):
        self.useSmtpHostTextCtrl.Enable(value)
        self.useSmtpPortSpinCtrl.Enable(value)

    def toggleAuthOptions(self, value):
        self.useAuthUserTextCtrl.Enable(value)
        self.useAuthPassTextCtrl.Enable(value)

    def onCancel(self, e):
        self.printMessage("Operation aborted (waiting for thread to die)\n", WARNING)
        self.abortEvent.set()

    def onOk(self, e):
        if self.panel.Validate():
            self.startSession()
            delayedresult.startWorker(consumer=self._consumer, workerFn=self._worker)

    def printMessage(self, msg, type=NOTSET):
        #FIXME: on windows, the screen appears to clear during auto-scroll
        wx.CallAfter(self.resultsTextCtrl.SetDefaultStyle, wx.TextAttr(colText=type))
        wx.CallAfter(self.resultsTextCtrl.AppendText, msg)
        wx.CallAfter(self.resultsTextCtrl.SetDefaultStyle, wx.TextAttr(colText=wx.SystemSettings_GetColour(wx.SYS_COLOUR_WINDOWTEXT)))

    def startSession(self):
        self.resultsTextCtrl.Clear()
        self.toggleWorkingMode(True)
        self.abortEvent.clear()
        self.printMessage("Session started: %s\n" % time.strftime("%Y-%m-%d %H:%M:%S"))

    def endSession(self):
        self.toggleWorkingMode(False)
        self.printMessage("Session ended: %s\n" % time.strftime("%Y-%m-%d %H:%M:%S"))

    def _resultConsumer(self, delayedResult):
        assert delayedResult.getJobID() == self.jobID
        try:
            result = delayedResult.get()
        except:
            traceback.print_exc()
        self.endSession()

    def _worker(self):
        mailFrom = self.mailFromTextCtrl.GetValue()
        mailTo = self.mailToTextCtrl.GetValue()
        mailMsg = self.mailMsgTextCtrl.GetValue()
        useNsHost = self.useNsHostTextCtrl.GetValue()
        useNsPort = self.useNsPortSpinCtrl.GetValue()
        nsQueryTimeout = self.nsQueryTimeoutSpinCtrl.GetValue()
        useNsTcp = self.useNsTcpCheckBox.GetValue()
        useSmtpHost = self.useSmtpHostTextCtrl.GetValue()
        useSmtpPort = self.useSmtpPortSpinCtrl.GetValue()
        smtpConnectTimeout = self.smtpConnectTimeoutSpinCtrl.GetValue()
        useSmtpHelo = self.useSmtpHeloTextCtrl.GetValue()
        useAuthUser = self.useAuthUserTextCtrl.GetValue()
        useAuthPass = self.useAuthPassTextCtrl.GetValue()

        wx.CallAfter(self.printMessage, "Sender: %s\n" % mailFrom, INFO)
        wx.CallAfter(self.printMessage, "Recipient: %s\n" % mailTo, INFO)
        wx.CallAfter(self.printMessage, "Message size: %d bytes\n" % len(mailMsg), INFO)

        # Set name servers
        resolver = dns.resolver.Resolver()
        resolver.lifetime = nsQueryTimeout
        if self.useNsCheckBox.IsChecked():
            resolver.nameservers = []
            if util.is_ip(useNsHost):
                resolver.nameservers.append(useNsHost)
            else:
                try:
                    wx.CallAfter(self.printMessage, "Resolving IP address for nameserver %s\n" % useNsHost, ACTION)
                    resolver.nameservers.append(socket.gethostbyname(useNsHost))
                except socket.gaierror, e:
                    wx.CallAfter(self.printMessage, "Unable to resolve IP address for nameserver %s\n" % useNsHost, WARNING)
            resolver.port = useNsPort
        else:
            resolver.port = DNS_DEFAULT_PORT
        nsHosts = []
        for nsHost in resolver.nameservers:
            if useNsTcp:
                nsHosts.append("%s:%d (TCP)" % (nsHost, resolver.port))
            else:
                nsHosts.append("%s:%d" % (nsHost, resolver.port))
        if len(nsHosts) > 0:
            wx.CallAfter(self.printMessage, "Using name servers: %s\n" % (', '.join(nsHosts)), INFO)

        # Get SMTP host(s)
        if not self.abortEvent():
            smtpHosts = []
            if self.useSmtpCheckBox.IsChecked():
                smtpHosts = map(string.strip, useSmtpHost.split(','))
            else:
                domain = ''.join(mailTo.split('@')[1:])
                smtpHosts = self.dnsQuery(resolver, domain, 'MX', useNsTcp)
            if len(smtpHosts):
                wx.CallAfter(self.printMessage, "Using SMTP servers: %s\n" % (','.join(smtpHosts)), INFO)

        for smtpHost in smtpHosts:

            # Resolve SMTP Host
            if not self.abortEvent():
                if util.is_ip(smtpHost):
                  smtpHostResolved = smtpHost
                else:
                  answers = self.dnsQuery(resolver, smtpHost, 'A', useNsTcp)
                  if len(answers):
                      smtpHostResolved = answers[0] # Only use first returned address
                  else:
                      break # Give up if smtp host could not be resolved

                # Append port to smtp server address
                if self.useSmtpCheckBox.IsChecked():
                    smtpHostResolved += ':' + str(useSmtpPort)
                else:
                    smtpHostResolved += ':' + str(SMTP_DEFAULT_PORT)

            # Connect and send message
            if not self.abortEvent():
                wx.CallAfter(self.printMessage, "Connecting to SMTP server: %s\n" % smtpHostResolved, ACTION)
                try:
                    smtp = smtplib.SMTP(smtpHostResolved, timeout=smtpConnectTimeout)
                    smtp.set_debuglevel(SMTP_DEBUGLEVEL)
                    if self.useTlsCheckBox.IsChecked():
                        wx.CallAfter(self.printMessage, "Starting TLS\n", ACTION)
                        if smtp.has_extn('STARTTLS'):
                            smtp.starttls()
                        else:
                            wx.CallAfter(self.printMessage, "TLS not supported by server\n", WARNING)
                    wx.CallAfter(self.printMessage, "Sending HELO/EHLO: %s\n" % useSmtpHelo, ACTION)
                    smtp.ehlo_or_helo_if_needed()
                    if self.useAuthCheckBox.IsChecked():
                        wx.CallAfter(self.printMessage, "Authenticating as: %s\n" % useAuthUser, ACTION)
                        smtp.login(useAuthUser, useAuthPass)
                    wx.CallAfter(self.printMessage, "Sending message\n", ACTION)
                    smtp.sendmail(mailFrom, mailTo, mailMsg)
                    smtp.quit()
                    wx.CallAfter(self.printMessage, "Message accepted\n", RESULT)
                    break
                except socket.error: # should be SMTPConnectError - http://bugs.python.org/issue2118
                    wx.CallAfter(self.printMessage, "Connection timed out after %d second(s)\n" % smtpConnectTimeout, ERROR)
                    continue
                except smtplib.SMTPResponseException, e:
                    wx.CallAfter(self.printMessage, "%d %s\n" % (e.smtp_code, e.smtp_error), ERROR)
                    break
                except smtplib.SMTPRecipientsRefused, e:
                    for recipient, msg in e.recipients.items():
                        wx.CallAfter(self.printMessage, "%d %s\n" % msg, ERROR)
                    break
                except smtplib.SMTPException, e:
                    wx.CallAfter(self.printMessage, "%s\n" % e, ERROR)
                    break

    def _consumer(self, result):
        try:
            result.get()
        except:
            traceback.print_exc()
        self.endSession()

    #FIXME: needs cleanup
    def dnsQuery(self, resolver, qname, rdtype, tcp=False):
        wx.CallAfter(self.printMessage, "Looking up %s records for %s\n" % (rdtype, qname), ACTION)
        results = []
        try:
            answers = resolver.query(qname=qname, rdtype=rdtype, tcp=tcp)
            if rdtype.upper() == 'MX':
                mxData = []
                for rdata in answers:
                    wx.CallAfter(self.printMessage, "Got answer: %s (TTL=%d)\n" % (rdata.to_text(), answers.ttl), RESULT)
                    mxData.append((rdata.preference, str(rdata.exchange).rstrip('.')))
                mxData.sort()
                for mxPref, mxHost in mxData:
                    results.append(mxHost)
            else:
                for rdata in answers:
                    wx.CallAfter(self.printMessage, "Got answer: %s (TTL=%d)\n" % (rdata.to_text(), answers.ttl), RESULT)
                    results.append(rdata.to_text().rstrip('.'))
        except dns.resolver.NoNameservers:
            wx.CallAfter(self.printMessage, "No name servers defined\n", ERROR)
        except dns.resolver.Timeout:
            wx.CallAfter(self.printMessage, "Query timed out after %d second(s)\n" % resolver.lifetime, ERROR)
        except dns.resolver.NXDOMAIN:
            wx.CallAfter(self.printMessage, "Domain does not exist (NXDOMAIN)\n", ERROR)
        except dns.resolver.NoAnswer:
            if rdtype.upper() == 'MX':
                wx.CallAfter(self.printMessage, "No MX records found -- First A record will be used as " +
                    "implicit MX record with preference of 0 (per RFC 2821 section 5)\n", RESULT)
                results.append(qname)
            else:
                wx.CallAfter(self.printMessage, "No %s records found\n" % rdtype, ERROR)
        except dns.rdatatype.UnknownRdatatype:
            wx.CallAfter(self.printMessage, "Unknown record type\n", ERROR)
        return results

    def getMyEmailAddress(self):
        return ("%s@%s") % (getpass.getuser(), '.'.join(socket.getfqdn().split('.')[1:]))

    def getRandomText(self, words=100, word_min=1, word_max=15):
        result = []
        for word in range(1, words + 1):
            result.append(''.join(random.sample(string.letters,random.randrange(word_min, word_max))))
        return ' '.join(result)
