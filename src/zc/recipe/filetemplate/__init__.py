import os
import re
import stat
import zc.buildout.buildout


class FileTemplate(object):

    defaults = dict(
        marker='$',
        source='',
        destination='.',
        suffix='.in',
        )

    def __init__(self, buildout, name, options):
        self.buildout = buildout
        self.name = name
        self.options = options
        source = self.options.get(
            'source-directory', self.defaults['source']
            ).strip('/').replace('../', '')
        destination = self.options.get(
            'destination-directory', self.defaults['destination']
            ).strip('/').replace('../', '')
        suffix = self.options.get('suffix', self.defaults['suffix'])
        options['destination-directory'] = destination
        options['source-directory'] = source
        options['suffix'] = suffix
        self.results = {}
        # We have to cook the results early to ensure references to
        # other parts from within the template are recognized as
        # dependencies.  Since we always generate the files, updates to
        # keys from non-part sections are handled correctly as well.
        self.cook()

    def cook(self):
        options = self.options
        root = self.buildout['buildout']['directory']
        files = options['files'].split()

        for name in files:
            path = os.path.join(
                root, options['source-directory'], name) + options['suffix']
            text = open(path).read().strip()
            o = zc.buildout.buildout.Options(
                self.buildout, self.name, dict(text=self.decorate(text)))
            o._initialize()
            text = self.undecorate(o['text'])
            path = os.path.join(root, options['destination-directory'], name)
            self.results[path] = text

    def install(self):
        for path, text in self.results.items():
            missing = missing_paths(path)
            if missing:
                os.makedirs(os.path.dirname(path))
            out = open(path, 'w')
            out.write(text)
            out.close()
            # self.options.created(path)
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

    def __init__(self, buildout, name, options):
        if 'destination-directory' not in options:
            # Use the buildout's bin-directory, relative to the buildout:
            bin_directory = buildout['buildout']['bin-directory']
            buildout_directory = buildout['buildout']['directory']
            bin_directory = bin_directory[len(buildout_directory):]
            if bin_directory[0] in r'\/':
                bin_directory = bin_directory[1:]
            options['destination-directory'] = bin_directory
        super(ScriptTemplate, self).__init__(buildout, name, options)

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


def missing_paths(path):
    p = os.path.dirname(path)
    if os.path.exists(p):
        return []
    return (missing_paths(p)).insert(0, p)
