"""
payload_transfer_factory.py

Copyright 2006 Andres Riancho

This file is part of w3af, http://w3af.org/ .

w3af is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation version 2 of the License.

w3af is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with w3af; if not, write to the Free Software
Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

"""
import w3af.core.controllers.output_manager as om

from w3af.core.controllers.exceptions import BaseFrameworkException
from w3af.core.controllers.payload_transfer.echo_windows import EchoWindows
from w3af.core.controllers.payload_transfer.echo_linux import EchoLinux
from w3af.core.controllers.payload_transfer.reverse_ftp import ReverseFTP
from w3af.core.controllers.payload_transfer.clientless_reverse_http import ClientlessReverseHTTP
from w3af.core.controllers.extrusion_scanning.extrusionScanner import extrusionScanner
from w3af.core.controllers.intrusion_tools.execMethodHelpers import os_detection_exec


class payload_transfer_factory(object):
    """
    This factory is pretty cool stuff, it uses an exec_method ( generated by
    os commanding, or some other vuln ) to determine what is the fastest method
    to send something to the compromised host. After determining what method to
    use, it will return the fastest method.

    Transfers methods inherit from transfer factory and can be found in this
    directory. If you want to add a new method, you should create the file and
    add it to the to_test list that is defined in the first lines of this
    function.
    """
    def __init__(self, exec_method):
        self._exec_method = exec_method
        self._es = extrusionScanner(exec_method)

    def estimate_transfer_time(self):
        if self._es.can_scan():
            return self._es.estimate_scan_time() + 1
        else:
            return 1

    def get_transfer_handler(self, inbound_port=None):
        """
        Perform an extrusion scan and return a handler that will know how to
        upload files to the remote end. If the caller sends an inbound_port,
        don't perform an extrusion scan, just trust him and use that port.

        :param inbound_port: The port that we should use for reverse connections
        :return: An object with a "transfer" method, which can be called by the
                 user in order to upload files.
        """
        os = os_detection_exec(self._exec_method)
        if os == 'windows':
            echo_transfer = EchoWindows(self._exec_method, os)
        elif os == 'linux':
            echo_transfer = EchoLinux(self._exec_method, os)
        else:
            echo_transfer = EchoLinux(self._exec_method, os)

        to_test = [echo_transfer]
        try:
            if not inbound_port:
                inbound_port = self._es.get_inbound_port()
        except BaseFrameworkException, w3:
            msg = ('The extrusion scan failed, no reverse connect transfer '
                   'methods can be used. Trying inband echo transfer method.'
                   ' Error: "%s"')
            om.out.error(msg % w3)
        except Exception, e:
            om.out.error('Unhandled exception: "%s"' % e)
        else:
            to_test.append(ReverseFTP(self._exec_method, os, inbound_port))
            if os == 'windows':
                # FIXME: Need to add something here!
                pass
            elif os == 'linux':
                reverse = ClientlessReverseHTTP(self._exec_method, os,
                                                inbound_port)
                to_test.append(reverse)

            # Test the fastest first and return the fastest one...
            def sort_function(x, y):
                return cmp(y.get_speed(), x.get_speed())
            to_test.sort(sort_function)

        for method in to_test:

            om.out.debug('Testing if "%s" is able to transfer a file to the '
                         'compromised host.' % method)
            if method.can_transfer():
                om.out.debug('%s is able to transfer a file to the compromised'
                             ' host.' % method)
                return method
            else:
                om.out.debug('%s *FAILED* to transfer a file to the'
                             ' compromised host.' % method)

        raise BaseFrameworkException('Failed to transfer the file to the remote'
                                     ' host. All the transfer methods failed.'
                                     ' See the debug log for more information'
                                     ' and potential workarounds for this'
                                     ' issue.')