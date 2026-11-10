#!/usr/bin/env python3
"""Build inspectable demo repositories with Python 3 and Git >= 2.38.
Usage: python3 pull-request-diffs.py [NEW_OUTPUT_DIRECTORY]
Creates repos plus data.json; never modifies an existing directory.
"""
import json, os, pathlib, subprocess, sys, tempfile
ROOT = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path(tempfile.mkdtemp(prefix='pr-diff-fixtures-')) / 'examples'
ROOT.mkdir(parents=True, exist_ok=False)
ENV = dict(os.environ, GIT_CONFIG_NOSYSTEM='1', GIT_CONFIG_GLOBAL=os.devnull, GIT_AUTHOR_DATE='2026-01-01T00:00:00Z', GIT_COMMITTER_DATE='2026-01-01T00:00:00Z')
GAP = '# Connection settings\n# Shared configuration\n# Values in seconds\n# Retry policy\n'
def config(t, r, gap=GAP): return f'timeout = {t}\n{gap}retries = {r}\n'
DATA = {}
for name in ['same','independent','conflict','semantic','stale','rename','squash']:
    repo = ROOT / name; repo.mkdir()
    def run(*args, check=True):
        return subprocess.run(['git', '-c', 'core.autocrlf=false', '-c', 'commit.gpgsign=false', *args], cwd=repo, env=ENV, text=True, capture_output=True, check=check)
    def git(*args): return run(*args).stdout.strip()
    def write(files):
        for p in repo.glob('*.py'): p.unlink()
        for p, value in files.items(): (repo / p).write_text(value)
        git('add','-A')
    def commit(message): git('commit','--allow-empty','-m',message)
    git('init','-b','main'); git('config','user.name','PR Diff Example'); git('config','user.email','example@example.invalid')
    b={'config.py': config(10,3)}; f={'config.py':config(20,3)}; m={'config.py':config(10,5)}
    if name in ['same','squash','stale']:
        b={'config.py':'feature_enabled = False\n'}; f={'config.py':'feature_enabled = True\n'}; m=f.copy()
    if name=='conflict': b={'config.py':config(10,3,'')}; f={'config.py':config(20,3,'')}; m={'config.py':config(10,5,'')}
    if name=='semantic':
        b={'api.py':'def greet(name):\n    return "Hello " + name\n','app.py':'from api import greet\nprint(greet("Ada"))\n'}
        f={**b,'app.py':'from api import greet\nprint(greet("Grace"))\n'}
        m={'api.py':'def greet(first, last):\n    return "Hello " + first + " " + last\n','app.py':'from api import greet\nprint(greet("Ada", "Lovelace"))\n'}
        # Separate callers: each branch runs, their combination adds an obsolete call.
        f={**b,'new_client.py':'from api import greet\nprint(greet("Grace"))\n'}
    if name=='rename': f={'settings.py':config(10,3)}
    write(b);commit('A: common ancestor');git('tag','ancestor');git('checkout','-b','feature');write(f);commit('F: feature change');git('checkout','main')
    old=None
    if name=='stale': old=git('merge-tree','--write-tree','main','feature')
    if name=='squash': git('merge','--squash','feature');commit('M: squash feature without its ancestry')
    else: write(m);commit('M: target change')
    def tree(ref):
        return {p:run('show',f'{ref}:{p}').stdout for p in git('ls-tree','-r','--name-only',ref).splitlines()}
    result=run('merge-tree','--write-tree','main','feature',check=False)
    assert result.returncode==(1 if name=='conflict' else 0),result.stdout
    tree_id=result.stdout.splitlines()[0]
    def diff(a,z): return run('diff','--no-ext-diff','--no-color','--find-renames',a,z).stdout
    item={'base':tree('ancestor'),'feature':tree('feature'),'target':tree('main'),'result':tree(tree_id),'direct':diff('main','feature'),'conventional':diff('ancestor','feature'),'delta':None if result.returncode else diff('main',tree_id),'conflictOutput':result.stdout if result.returncode else '', 'history':git('log','--all','--graph','--oneline','--decorate')}
    if name in ['same','squash','stale']: assert item['delta']=='' and item['conventional']
    if name=='independent': assert item['result']=={'config.py':config(20,5)}
    if name=='rename': assert item['result']=={'settings.py':config(10,5)}
    if old: item['oldResult']=tree(old);item['oldDelta']=diff('ancestor',old)
    if name=='semantic':
        for ref,entry in [('feature','new_client.py'),('main','app.py'),(tree_id,'new_client.py')]:
            sandbox=pathlib.Path(tempfile.mkdtemp(prefix='pr-diff-run-'))
            for p,v in tree(ref).items(): (sandbox/p).write_text(v)
            check=subprocess.run([sys.executable,entry],cwd=sandbox,text=True,capture_output=True)
            assert (check.returncode!=0)==(ref==tree_id)
            if ref==tree_id: item['runtimeError']=check.stderr.splitlines()[-1]
    DATA[name]=item
(ROOT/'data.json').write_text(json.dumps(DATA,indent=2))
print(f'Verified seven scenarios with {git("--version")}. Repositories and data: {ROOT}')
