import json, os, tempfile, threading, unittest, urllib.error, urllib.request
from http.server import ThreadingHTTPServer
import server

class AppTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory();server.DB=server.Path(cls.tmp.name)/'test.db';server.init_db();cls.http=ThreadingHTTPServer(('127.0.0.1',0),server.App);cls.port=cls.http.server_port;threading.Thread(target=cls.http.serve_forever,daemon=True).start()
    @classmethod
    def tearDownClass(cls):cls.http.shutdown();cls.tmp.cleanup()
    def req(self,path,method='GET',data=None,cookie=None):
        headers={'Content-Type':'application/json'}
        if cookie:headers['Cookie']=cookie
        r=urllib.request.urlopen(urllib.request.Request(f'http://127.0.0.1:{self.port}{path}',data=json.dumps(data).encode() if data is not None else None,headers=headers,method=method));return r,json.loads(r.read())
    def test_account_task_and_autosave_flow(self):
        r,_=self.req('/api/auth/register','POST',{'name':'Ana','email':'ana@example.com','password':'segredo123'});cookie=r.headers['Set-Cookie'].split(';')[0]
        _,task=self.req('/api/tasks','POST',{'title':'Pesquisa','subject':'História','prompt':'Explique o tema.'},cookie);self.assertEqual(task['title'],'Pesquisa')
        _,saved=self.req(f"/api/tasks/{task['id']}/draft",'PUT',{'draft':'Meu rascunho'},cookie);self.assertEqual(saved['draft'],'Meu rascunho')
        _,done=self.req(f"/api/tasks/{task['id']}",'PATCH',{'done':True},cookie);self.assertTrue(done['done'])
        _,tasks=self.req('/api/tasks',cookie=cookie);self.assertEqual(len(tasks),1)
    def test_private_routes_require_login(self):
        with self.assertRaises(urllib.error.HTTPError) as e:self.req('/api/tasks')
        self.assertEqual(e.exception.code,401)
        e.exception.close()
if __name__=='__main__':unittest.main()
