from chemdataextractor.parse.base import BaseSentenceParser
from chemdataextractor.parse import join, R, merge, W, Optional
from chemdataextractor.utils import first

import re

'''
chemdataextractor.parse.bioactive_units
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Bioactivity units text parser.

Ki = 50nM
Ki of 50nM
high Ki (50nM)
50nM --> 50 ng/uL (?)
'''
molar_unit = R('^[YZEPTGMkhcm\u03BC\u00B5unpfzyad]?M$')
mass_unit = R('^[YZEPTGMkhcm\u03BC\u00B5unpfzyad]?(mol|g)$') 
volume_unit = R('^[YZEPTGMkhcm\u03BC\u00B5unpfzyad]?(mol|l|L)$')
units = ((molar_unit | mass_unit + W('/') + volume_unit).add_action(merge))('units').add_action(join)

value_units = (R('\d+') + Optional(W(' ')) + units).add_action(join)

ic_ki = R('ki|ic50|ec50|ed50|ld50|sc50|mic', re.I)


#TO DO: to detect values range. i.e, 150-180 ug/mL or similar.

bioact_units = (((ic_ki + Optional(W(' ')) + W('=')).add_action(merge)).hide() + value_units)('biounits').add_action(join)

class BioUnitsParser(BaseSentenceParser):
    
    root = bioact_units

    def interpret(self, result, start, end):

        activity = self.model(units=first(result.xpath('./text()')))

        yield activity