from __future__ import absolute_import

import re

import wx

from . import util


VALIDATE_FQDN=1
VALIDATE_IP=2
VALIDATE_ALPHA=4
VALIDATE_NUM=8
VALIDATE_NOT_NULL=16


class BaseValidator(wx.PyValidator):

    def __init__(self, *args, **kwargs):
        wx.PyValidator.__init__(self, *args, **kwargs)

    def WxErrorDialog(self, msg):
        self.win.SetBackgroundColour('#ffcccc')
        self.win.SetFocus()
        self.win.Refresh()
        wx.MessageBox(msg, "Error")

    def WxClearErrorDialog(self):
        self.win.SetBackgroundColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_WINDOW))
        self.win.Refresh()


class GenericTextValidator(BaseValidator):

    def __init__(self, flag=None):
        self.flag = flag
        BaseValidator.__init__(self)

    def Clone(self):
        return GenericTextValidator(flag=self.flag)

    def Validate(self, win):
        self.win = self.GetWindow()
        if self.win.IsEnabled():
            result = False
            self.text = self.win.GetValue()
            if self.flag == VALIDATE_ALPHA:
                if self.ValidateAlpha():
                    result = True
                else:
                    self.WxErrorDialog("Only letters are allowed.")
            elif self.flag == VALIDATE_NUM:
                if self.ValidateNum():
                    result = True
                else:
                    self.WxErrorDialog("Only numbers are allowed.")
            else:
                if self.ValidateNotNull():
                    result = True
                else:
                    self.WxErrorDialog("A value is required.")
            if result:
                self.WxClearErrorDialog()
        else:
            result = True

        return result

    def ValidateAlpha(self):
        return re.search("^[a-z]+$", self.text, re.IGNORECASE)

    def ValidateNumeric(self):
        return re.search("^[0-9]+$", self.text)

    def ValidateNotNull(self):
        return re.search("^.+$", self.text)


class HostAddressValidator(BaseValidator):

    def __init__(self, flag=None):
        self.flag = flag
        BaseValidator.__init__(self)

    def Clone(self):
        return HostAddressValidator(flag=self.flag)

    def Validate(self, win):
        self.win = self.GetWindow()
        if self.win.IsEnabled():
            result = False
            self.text = self.win.GetValue()
            if self.flag == VALIDATE_IP:
                if self.ValidateIP():
                    result = True
                else:
                    self.WxErrorDialog("A valid IP address is required.")
            elif self.flag == VALIDATE_FQDN:
                if self.ValidateFQDN():
                    result = True
                else:
                    self.WxErrorDialog("A valid FQDN is required.")
            else:
                if self.ValidateIP() or self.ValidateFQDN():
                    result = True
                else:
                    self.WxErrorDialog("A valid IP address or FQDN is required.")
            if result:
                self.WxClearErrorDialog()
        else:
            result = True

        return result

    def ValidateIP(self):
        result = False
        if util.is_ip(self.text):
            result = True
        return result

    def ValidateFQDN(self):
        return re.search("^[0-9a-z\-\.]+$", self.text)


class EmailAddressValidator(BaseValidator):

    def __init__(self):
        BaseValidator.__init__(self)

    def Clone(self):
        return EmailAddressValidator()

    def Validate(self, win):
        self.win = self.GetWindow()
        if self.win.IsEnabled():
            result = False
            text = self.win.GetValue()
            if re.search("^\S+@\S+$", text):
                self.WxClearErrorDialog()
                result = True
            else:
                self.WxErrorDialog("A valid email address is required.")
        else:
            result = True
        return result
