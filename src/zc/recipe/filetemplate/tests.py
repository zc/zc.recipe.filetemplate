import doctest
import zc.buildout.testing
import zope.testing.renormalizing

def setUp(test):
    zc.buildout.testing.buildoutSetUp(test)
    zc.buildout.testing.install_develop('zc.recipe.filetemplate', test)


def test_suite():
    return doctest.DocFileSuite(
        'README.txt',
        setUp=setUp,
        tearDown=zc.buildout.testing.buildoutTearDown,
        checker=zope.testing.renormalizing.RENormalizing([
            zc.buildout.testing.normalize_path,
            ]),
        optionflags=(doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE),
        )
