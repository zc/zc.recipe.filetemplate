import os
import re
import stat
import zc.buildout.buildout


class FileTemplate(object):

    defaults = dict(
        marker='$',
        source='',
        suffix='.in',
        )

    default_desination_key = 'directory'

    def __init__(self, buildout, name, options):
        self.buildout = buildout
        self.name = name
        self.options = options
        source = self.options.get(
            'source-directory', self.defaults['source']
            )
        destination = self.options.get('destination-directory')
        if not destination:
            dep = deployment(buildout, options)
            if dep:
                destination = dep['etc-directory']
            else:
                destination = buildout['buildout'][self.default_desination_key]
        suffix = self.options.get('suffix', self.defaults['suffix'])
        options['destination-directory'] = destination
        options['source-directory'] = source
        options['suffix'] = suffix
        self.results = {}
        # We have to cook the results early to ensure references to
        # other parts from within the template are recognized as
        # dependencies.  Since we always generate the files, updates to
        # keys from non-part sections are handled correctly as well.
        options = self.options
        root = self.buildout['buildout']['directory']
        files = options['files'].split()

        for name in files:
            path = os.path.join(root, source, name) + suffix
            text = open(path).read().strip()
            o = zc.buildout.buildout.Options(
                self.buildout, self.name, dict(text=self.decorate(text)))
            o._initialize()
            text = self.undecorate(o['text'])
            path = os.path.join(root, destination, name)
            self.results[path] = text

    def install(self):
        for path, text in self.results.items():
            missing = missing_paths(path)
            if missing:
                os.makedirs(os.path.dirname(path))
            out = open(path, 'w')
            out.write(text)
            out.close()
            self.options.created(path, *missing)

        return self.options.created()

    update = install

    def decorate(self, text):
        """Decorate dollar signs in the template.

        1. Decorate the buildout markers (in case they contain '$').
        2. Decorate all the remaining dollar signs
           (e.g., shell variable substitutions) to protect them from
           substitution in the buildout options.
        3. Undecorate buildout markers and replace them with
           dollar signs, so that they can be substituted in the buildout
           options.

        """
        marker = re.escape(self.options.get('marker', self.defaults['marker']))
        return re.sub(
            '@BUILDOUT@',
            lambda x: '$',
            re.sub(
                r'\$',
                lambda x: '@DOLLAR@',
                re.sub(
                    marker + r'({[\w .-]*:[\w .-]+})',
                    lambda x: '@BUILDOUT@' + x.group(1),
                    text,
                    ),
                ),
            )

    def undecorate(self, text):
        return re.sub('@DOLLAR@', lambda x: '$', text)


class ScriptTemplate(FileTemplate):

    default_desination_key = 'bin-directory'

    def install(self):
        created = super(ScriptTemplate, self).install()
        for path in self.results:
            self.set_executable(path)
        return created

    def set_executable(self, path):
        mode = stat.S_IMODE(os.stat(path).st_mode)
        mode |= stat.S_IXUSR
        if mode & stat.S_IRGRP:
            mode |= stat.S_IXGRP
        if mode & stat.S_IROTH:
            mode |= stat.S_IXOTH
        os.chmod(path, mode)


def deployment(buildout, options):
    depname = options.get('deployment')
    if depname:
        return buildout[depname]
    else:
        return None


def missing_paths(path):
    p = os.path.dirname(path)
    if os.path.exists(p):
        return []
    return [p] + missing_paths(p)
