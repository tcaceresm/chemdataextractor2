from chemdataextractor.parse.base import BaseSentenceParser
from chemdataextractor.parse import I, join, R, merge, First, Or, Every, T, W, Optional
from chemdataextractor.utils import first

import re

'''
chemdataextractor.parse.biotarget
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Fungi names text parser.
'''

#Parser for target


targets = open(r'G:\Mi unidad\UC\9no Semestre\Proyecto data science\code\test\fungis_genres.txt', 'r')
genre_names = targets.read().split(',')
targets.close()

against = Optional(I('against')).hide()

abb_name = (against + (R('[A-Z]') + W('.')).add_action(merge) + R('[a-z]+')).add_action(join)

target_phrase = (abb_name | (against + First(genre_names)).add_action(join))('tgt')

# target_phrase = (abb_name.add_action(join))('tgt')


class TargetParser(BaseSentenceParser):
    
    root = target_phrase

    def interpret(self, result, start, end):

        activity = self.model(target=first(result.xpath('./text()')))

        yield activity




