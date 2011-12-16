import os
import re
import stat
import zc.buildout.buildout


class FileTemplate(object):

    defaults = dict(
        marker='$',
        source='',
        destination='bin',
        suffix='.in',
        executable=True,
        )

    def __init__(self, buildout, name, options):
        self.buildout = buildout
        self.name = name
        self.options = options

    def install(self):
        root = self.buildout['buildout']['directory']
        source = self.options.get(
            'source-directory', self.defaults['source']
            ).strip('/').replace('../', '')
        destination = self.options.get(
            'destination-directory', self.defaults['destination']
            ).strip('/').replace('../', '')
        suffix = self.options.get('suffix', self.defaults['suffix'])

        files = self.options.get('files', '').split()
        for name in files:
            path = os.path.join(root, source, name) + suffix
            text = open(path).read().strip()
            o = zc.buildout.buildout.Options(
                self.buildout, self.name, dict(text=self.decorate(text)))
            o._initialize()
            self.options[name + '-text'] = self.undecorate(o['text'])
            path = os.path.join(root, destination, name)
            # XXX: Ask Jim if it's necessary to record every single path part
            # in options.created.  If not, this condition should suffice.
            # if not os.path.exists(os.path.dirname(path)):
            missing = missing_paths(path)
            if missing:
                os.makedirs(os.path.dirname(path))
            out = open(path, 'w')
            out.write(self.options[name + '-text'])
            out.close()
            self.set_permissions(path)
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

    def set_permissions(self, path):
        executable = boolean(
            self.options.get('execute-mode', self.defaults['executable']))
        if executable:
            mode = stat.S_IMODE(os.stat(path).st_mode)
            mode |= stat.S_IXUSR
            if mode & stat.S_IRGRP:
                mode |= stat.S_IXGRP
            if mode & stat.S_IROTH:
                mode |= stat.S_IXOTH
            os.chmod(path, mode)


_booleans = {
    'yes': True, 'true': True, 'on': True, '1': True,
    'no': False, 'false': False, 'off': False, '0': False,
    }


def boolean(setting):
    try:
        return _booleans[str(setting).lower()]
    except KeyError:
        raise ValueError('Invalid Boolean setting: %r' % (setting,))

def missing_paths(path):
    p = os.path.dirname(path)
    if os.path.exists(p):
        return []
    return (missing_paths(p)).insert(0, p)
