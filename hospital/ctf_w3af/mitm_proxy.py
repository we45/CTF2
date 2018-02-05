from mitmproxy.models import decoded
import base64
import netlib
from mitmproxy import controller, proxy
from mitmproxy.proxy.server import ProxyServer


class we45MitmProxy(controller.Master):
    def __init__(self, server, base64_path,kwargs):        
        self.data  = []        
        self.out_base64 = base64_path
        controller.Master.__init__(self, server)        
        self.ignore_ext = kwargs.get('ignore_ext',[])
        self.ignore_domain = kwargs.get('ignore_domain',[])

    def run(self):
        return controller.Master.run(self)          

    def handle_request(self, flow):
        req_url = flow.request.url
        an_unwanted_extension = any(ext for ext in self.ignore_ext if req_url.endswith(ext))
        an_unwanted_domain = any(st for st in self.ignore_domain if st in req_url)
        if an_unwanted_extension or an_unwanted_domain:
            pass
        else:
            # print "URL Request ====>",req_url
            with decoded(flow.request):
                self.data.append(base64.b64encode(netlib.http.http1.assemble_request(flow.request))) 
        flow.reply()               
                
    def load_data(self):
        with open(self.out_base64, 'wb') as f:
            for dd in self.data:
                f.write(b'{0}\n'.format(dd))
