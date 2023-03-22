import pytest
import importlib.metadata
from packaging import version as _v

class dependencyVersion(object):
    def __init__(self, packagename):
        self.packagename=packagename

    def dependencyVersionTest(self):
        return _v.parse(importlib.metadata.version(self.packagename))

def dependencyList():
    deplist={}
    with open('requirements.txt', 'r') as req:
        modlist=req.read()

    for mod in modlist.split():
        m,v=mod.split('==')

        # This is a hack to handle non-essential deps
        if m not in ['pyinstaller', 'PyWavelets']:
            deplist[m]=v

    return tuple(deplist)

@pytest.fixture 
def dependencyFixture(request):
    return dependencyVersion(request.param)

@pytest.mark.parametrize(
    'dependencyFixture',
    dependencyList(),
    indirect=True)
def test_DependencyVersion(dependencyFixture):
    assert dependencyFixture.dependencyVersionTest() == _v.parse(importlib.metadata.version(dependencyFixture.packagename))
