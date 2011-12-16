=========================
ZC Recipe Script Template
=========================

The `zc.recipe.filetemplate` recipe enables automated creation of
files from input templates.  The templates use the generic buildout
variable substitution.

Let's try a simple file for cleaning the development database.

    >>> write('clean.in', """\
    ... #!/bin/sh
    ... rm -f ${buildout:parts-directory}/zeo_server_main_database/Data.fs*
    ... rm -rf ${buildout:parts-directory}/zeo_server_main_database/blobs
    ... mkdir ${buildout:parts-directory}/zeo_server_main_database/blobs
    ... """)

The corresponding buildout configuration is very simple as well.

    >>> configuration = """\
    ... [buildout]
    ... parts = clean
    ...
    ... [clean]
    ... recipe = zc.recipe.filetemplate
    ... files = clean
    ... """

When we execute the buildout the substitution is embedded in the script.

    >>> def build(src=configuration, show=False):
    ...     write('buildout.cfg', src)
    ...     r = system(buildout)
    ...     if ('error' in r.lower()) or show:
    ...         print r,

    >>> build(show=True)
    Installing clean.

    >>> cat('bin', 'clean')
    #!/bin/sh
    rm -f /sample-buildout/parts/zeo_server_main_database/Data.fs*
    rm -rf /sample-buildout/parts/zeo_server_main_database/blobs
    mkdir /sample-buildout/parts/zeo_server_main_database/blobs

The script is executable and registered by buildout as installed.

    >>> print system('ls -l bin/clean')
    -rwx...bin/clean
    >>> print system('grep __buildout_installed__ .installed.cfg')
    __buildout_installed__ = /sample-buildout/bin/clean

2. Buildout substitution + $ signs

   - Perl script
   - sh script

3. Buildout substitution + ${xxx:-yyy} shell substitutions
4. Python script with regex $ signs (e.g., run it on ``__init.py__``)
5. Show that ``__buildout_installed__`` contains all the directories on
   the path that were not created before this is run (is this needed?)
6. What happens on update?
7. Show that different options work.
8. Show that the file is executable.
9. Run the script after creation! Separate recipe?
