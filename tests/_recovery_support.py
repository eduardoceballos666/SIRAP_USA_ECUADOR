"""Local durable fake of GitHub Contents CAS, never a real account or network."""
from __future__ import annotations

import base64
import hashlib
import sqlite3

from src import github_storage
from src.storage import HEADERS


class FakeGitHub:
    def __init__(self, path):
        self.path=str(path)
        self.fail_next=None
        with sqlite3.connect(self.path) as db:
            db.execute('CREATE TABLE IF NOT EXISTS files (name TEXT PRIMARY KEY, content TEXT, sha TEXT)')
            for name,columns in HEADERS.items():
                text=','.join(columns)+'\n'
                db.execute('INSERT OR IGNORE INTO files VALUES (?,?,?)',
                           (name+'.csv',text,self.sha(text)))

    @staticmethod
    def sha(text):
        return hashlib.sha256(text.encode()).hexdigest()

    def install(self, monkeypatch):
        monkeypatch.setenv('SIRAP_DATA_GITHUB_TOKEN','synthetic-test-token-not-a-credential')
        monkeypatch.setenv('SIRAP_GITHUB_REQUIRED','1')
        monkeypatch.setattr(github_storage,'_verify_private_repository',lambda:None)
        monkeypatch.setattr(github_storage,'_request',self.request)

    def request(self, method, path, payload=None):
        name=path.rsplit('/',1)[-1]
        assert name.removesuffix('.csv') in HEADERS, 'Unexpected synthetic storage path'
        fail=self.fail_next if method=='PUT' else None
        if fail:
            self.fail_next=None
        if fail=='before_put':
            raise github_storage.GitHubStorageError('Synthetic connection lost before commit')
        with sqlite3.connect(self.path,timeout=10) as db:
            if method=='PUT':
                db.execute('BEGIN IMMEDIATE')
            found=db.execute('SELECT content,sha FROM files WHERE name=?',(name,)).fetchone()
            if method=='GET':
                return None if found is None else dict(type='file',encoding='base64',sha=found[1],
                    content=base64.b64encode(found[0].encode()).decode())
            assert method=='PUT', 'Unexpected synthetic transport method'
            if (payload or {}).get('sha')!=(found[1] if found else None):
                raise github_storage.GitHubStorageError('Synthetic HTTP 409: concurrent write')
            text=base64.b64decode(payload['content']).decode()
            sha=self.sha(text)
            db.execute('INSERT OR REPLACE INTO files VALUES (?,?,?)',(name,text,sha))
        if fail=='after_put':
            raise github_storage.GitHubStorageError('Synthetic response lost after commit')
        return {'content':{'sha':sha}}

    def contents(self, name):
        with sqlite3.connect(self.path) as db:
            return db.execute('SELECT content FROM files WHERE name=?',(name+'.csv',)).fetchone()[0]
