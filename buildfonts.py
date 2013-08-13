from collections import defaultdict
import os.path
import re
import subprocess
import sys


class CollectFontNames:
    pref = re.compile('pref\("font\.(name(?:-list)?)\.([^\.]+)\.(.*?)", "(.*?)"')
    def __init__(self):
        class listdict(defaultdict):
            def __init__(self):
                defaultdict.__init__(self, list)
        self.fontnames = defaultdict(listdict)

    def write(self, content):
        if not content.startswith('pref("font.name'):
            return
        
        name_or_list, family, langgroup, fonts = self.pref.match(content).groups()
        if name_or_list == 'name':
            self.fontnames[langgroup][family].insert(0, fonts)
        else:
            self.fontnames[langgroup][family] += fonts.split(', ')

    def getFonts(self, langgroup):
        langgroup = langgroup.lower()
        if langgroup in self.fontnames:
            return self.fontnames[langgroup]
        if '-' in langgroup:
            langgroup = langgroup.split('-')[0]
            if langgroup in self.fontnames:
                return self.fontnames[langgroup]
        return self.fontnames['x-unicode']  # see GetLanguageGroup

moz_base = sys.argv[1]

sys.path.append(os.path.join(moz_base, 'config'))
from Preprocessor import preprocess

cf = CollectFontNames()
preprocess(includes=[open(os.path.join(moz_base, 'modules/libpref/src/init/all.js'))],
           defines={
               'ANDROID': True,
               'MOZ_WIDGET_GONK': True
            },
            output=cf,
    line_endings='lf')

class Lang2Langgroup:
    prop = re.compile('([a-z\-]+)=([a-z\-]+)')
    def __init__(self, path):
        content = open(path).read()
        self.l2l = dict(self.prop.findall(content))

    def langgroup(self, locale):
        return self.l2l.get(locale, locale)

ll = Lang2Langgroup(os.path.join(moz_base,
                                 'intl/locale/src/langGroups.properties'))

fonts = cf.getFonts(ll.langgroup(sys.argv[2]))


fontfiles = {}
for line in subprocess.check_output(['fc-scan', '-f', "%{family}^%{style}^%{file}\n",
                                     'moztt', 'base/data/fonts']).split('\n'):
    if not line:
        continue
    family, style, _file = line.split('^')
    if style == 'Regular':
        fontfiles[family] = _file

for family, _f in sorted(fonts.iteritems()):
    print family
    for __f in _f:
        subprocess.call(['fc-validate', '-l', sys.argv[2], fontfiles[__f]])

