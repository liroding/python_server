#!/usr/bin/python
# _*_ coding: utf-8 _*_
import os       #Python的标准库中的os模块包含普遍的操作系统功能
import re       #引入正则表达式对象
import urllib   #用于对URL进行编解码
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler      #导入HTTP处理相关的模块
import io,shutil 



 
 
#自定义处理程序，用于处理HTTP请求
class TestHTTPHandler(BaseHTTPRequestHandler):
  def handle_one_request(self):
  
       """Handle a single HTTP request.
  
  
  
       You normally don't need to override this method; see the class
  
       __doc__ string for information on how to handle specific HTTP
  
       commands such as GET and POST.
  
  
  
       """
  
       try:
  
           self.raw_requestline = self.rfile.readline(65537)
  
           if len(self.raw_requestline) > 65536:
  
               self.requestline = ''
  
               self.request_version = ''
  
               self.command = ''
  
               self.send_error(414)
  
               return
  
           if not self.raw_requestline:
  
               self.close_connection = 1
  
               return
  
           if not self.parse_request():
  
               # An error code has been sent, just exit
  
               return
  
           mname = 'do_' + self.command
  
           if not hasattr(self, mname):
  
               self.send_error(501, "Unsupported method (%r)" % self.command)
  
               return
  
           method = getattr(self, mname)
  
           print "before call do_Get"
  
           method()
  
           #增加 debug info 及 wfile 判断是否已经 close
  
           print "after call do_Get"
  
           if not self.wfile.closed:
  
               self.wfile.flush() #actually send the response if not already done.
  
           print "after wfile.flush()"
  
       except socket.timeout, e:
  
           #a read or a write timed out.  Discard this connection
  
           self.log_error("Request timed out: %r", e)
  
           self.close_connection = 1
  
           return




  def do_action(self, path, args):
        print(path)
        print(args)
        self.outputtxt(args )

  def outputtxt(self, content):
        
        self.send_response(200)  
        self.send_header("Content-type", "text/html")
 #       self.send_header("Content-Length", str(len(content)))  
        self.end_headers()  
        #shutil.copyfileobj(f,self.wfile)
        self.wfile.write(content)
    
#处理GET请求
  def do_GET(self):
        print('[LIRO-DEBUG] enter do_get')
        print(self.command )
        mpath,margs=urllib.splitquery(self.path)
        self.do_action(mpath, margs)

  def do_POST(self):
        print('[LIRO-DEBUG] enter do_post')
        print(self.command )
        mpath,margs=urllib.splitquery(self.path)
        datas = self.rfile.read(int(self.headers['content-length']))
        self.do_action(mpath, datas)
        
#多线程处理

class ThreadingHTTPServer(ThreadingMixIn,HTTPServer):

    pass

  
#启动服务函数
def start_server(port):
     print('[LIRO-DEBUG] enter start_server')
     http_server = HTTPServer(('', int(port)), TestHTTPHandler)
     http_server.serve_forever() #设置一直监听并接收请求
 
os.chdir('static') #改变工作目录到 static 目录
start_server(8888) #启动服务，监听8000端口
