#!/usr/bin/python
# _*_ coding: utf-8 _*_
import os       #Python的标准库中的os模块包含普遍的操作系统功能
import re       #引入正则表达式对象
import urllib   #用于对URL进行编解码
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler      #导入HTTP处理相关的模块
import io,shutil 
import threading
import socket

from SocketServer import ThreadingMixIn
import cgi
import json
from configobj import ConfigObj


PROJECT_ROOT = os.path.dirname(os.path.realpath(__file__))

class HandleCfgFile():
  def getkeyvalue(self,strline,key1,key2):
      pat = re.compile(key1+'(.*?)'+key2,re.S)
      result = pat.findall(strline)
      print (result)
      return result[0]

  def openfile(self,filename):
      print("Open File name:%s"%(filename))
      fd = open(filename,'r')
      return fd

  def tojsondata(self,filename):
        _list = []
        config = ConfigObj(filename,encoding='UTF8')
        print(config['ARG'])
        _list.append(config['ARG'])
        _list.append(config['CASE'])
        print("[LIRO-DEBUG] liststring = %s " % _list)
        jsonArr = json.dumps(_list, ensure_ascii=False)
        print("[LIRO-DEBUG] jsonstring = %s " % jsonArr)
        return jsonArr
        '''
        _fd = self.openfile(filename)
        _list = []
        with _fd as f:
            for line in f:
                _dict={}
                if 'name' in line:
                    _dict.update(name = self.getkeyvalue(line,'name =','--'))
                if 'data' in line:
                    _dict.update(data = self.getkeyvalue(line,'data =','--'))
                _list.append(_dict)
        print("[LIRO-DEBUG] liststring = %s " % _list)
        jsonArr = json.dumps(_list, ensure_ascii=False)
        print("[LIRO-DEBUG] jsonstring = %s " % jsonArr)
        _fd.close()
        return jsonArr
        '''
  def writebackcfgini(self,filename,newdata):  #newdata is list struct
	config = ConfigObj(filename,encoding='UTF8')

	for i in range(len(newdata)):
		print(newdata[i])
		for k,v in newdata[i].items():
			for data in config.items():
				_ITEM = data[0]    # [ ]
				_arg  = data[1]
				#print(_item)
				#print(_arg)
				for item in _arg:
					if k == item:
						print(k)
						print(_ITEM)
						print(config[_ITEM][k])
						config[_ITEM][k] = v
						config.write()
	

					
		

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
        print('[LIRO-DEBUG] path = %s' % path)
        print('[LIRO-DEBUG] args = %s' % args)
        self.outputtxt(path,args)

  
  def outputtxt(self, path,content):

       handleclass =  HandleCfgFile()
       self.send_response(200)  
       self.send_header("Content-type", "text/html")
       self.send_header("Access-Control-Allow-Origin", "*")
       self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
       self.send_header("Access-Control-Allow-Headers", "X-Requested-With") 
       self.end_headers()  

       
       if path == '/AppCfg.txt':
            print 'get the AppCfg.txt'
            print (PROJECT_ROOT)

            '''
            f = open(PROJECT_ROOT+ '/AppCfg.ini',"rb")
            for line in f.readlines():            # 输出文件内容
                
                self.wfile.write(line)
                
            f.close()
            '''
            jsonStr = handleclass.tojsondata(PROJECT_ROOT+ '/hifcfg.ini')
            self.wfile.write(jsonStr)
            
            return 0

       if path == '/id=1':    #app cfg submit
            print 'submit new cfg data to hifcfg.ini'
	    jsonobj = json.loads(content)  #string to jsonobj
	    #print(type(jsonobj))
	    #print(jsonobj)

	    handleclass.writebackcfgini(PROJECT_ROOT+ '/hifcfg.ini',jsonobj)
            '''
	    self.handleclass =  HandleCfgFile()
            jsonStr = handleclass.tojsondata(PROJECT_ROOT+ '/hifcfg.ini')
            self.wfile.write(jsonStr)
            '''
            return 0         
	
#       self.send_header("Content-Length", str(len(content)))  
 
       self.wfile.write('Client: %sn ' % str(self.client_address) )
       self.wfile.write('User-agent: %sn' % str(self.headers['user-agent']))
       self.wfile.write('Path: %sn'%self.path)
       self.wfile.write('Form data:n')


    
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

     http_server = ThreadingHTTPServer(('', int(port)),TestHTTPHandler)
     http_server.serve_forever() #设置一直监听并接收请求
     sys.exit(0)
 
os.chdir('static') #改变工作目录到 static 目录
start_server(8888) #启动服务，监听8000端口
