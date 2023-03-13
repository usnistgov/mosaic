import pytest
import importlib.metadata
from packaging import version as _v

def dependencyVersionTest(dep):
    return _v.parse(importlib.metadata.version(dep))

@pytest.fixture 
def dependencyList():
    deplist={}
    with open('requirements.txt', 'r') as req:
        modlist=req.read()

    for mod in modlist.split():
        m,v=mod.split('==')

        # This is a hack to handle non-essential deps
        if m not in ['pyinstaller', 'PyWavelets']:
            deplist[m]=v

    return deplist

def test_DependencyVersion(dependencyList):
    assert all(dependencyVersionTest(k) == _v.parse(dependencyList[k]) for k in dependencyList.keys())
