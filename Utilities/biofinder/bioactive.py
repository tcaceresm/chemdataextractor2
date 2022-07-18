from chemdataextractor.parse.base import BaseSentenceParser
from chemdataextractor.parse import I, join, R, merge, W, Optional
from chemdataextractor.utils import first

import re


adverbio = R('extremely|significantly|highly|extraordinarily|excellently|moderately|strongly|very|greatly', re.I)

adjetivo = R('extreme|significant|high|extraordinary|excellent|moderate|very|strong|good|potent|great', re.I)

active = R('(bio)?active|effective|potent|strong', re.I)

activity = R('(bio)?activity|(bio)?activities|inhibition', re.I)

antifungal = R('antifungal|fungistatic|fungicidal', re.I)

effect = R('effects?', re.I)

inhibited = R('inhibit(ed)?', re.I)
eradicated = R('eradicated?', re.I)
growth = (inhibited + I('the') + I('growth')).add_action(join)

growth_inh = (I('growth') + I('inhibition')).add_action(join)

target_abb = ((R('[A-Z]') + W('.')).add_action(merge) + R('[a-z]+')).add_action(join)

#X drug showed extremely high bioactivity
bioact1 = (adverbio + adjetivo + Optional(antifungal) + activity).add_action(join)

#X drug showed high bioactivity
bioact2 = (adjetivo + Optional(antifungal) + activity).add_action(join)

#X drug is bioactive
bioact3 = (active)

#X drug inhibited -target-  (colony) growth|infection
bioact4 = (inhibited + target_abb.hide() + Optional(I('colony')) + (I('growth') | R('infections?', re.I))).add_action(join)

#X drug showed antifungal effect
bioact5 = (antifungal + effect).add_action(join)

#X drug significantly inhibit the growth
bioact6 = (adverbio + growth.hide()).add_action(join)

#X drug can inhibit -target-
bioact7 = (inhibited + target_abb.hide()).add_action(join)

#X drug showed antifungal activity
bioact8 = (antifungal + activity).add_action(join)

#X drug eradicated -target-
bioact9 = (eradicated + target_abb.hide()).add_action(join)


bioactivity = (bioact1 | bioact2 | bioact3 | bioact4 | bioact5 | bioact6 | bioact7 | bioact8 | bioact9)('bioactivity')

class BioactiveParser(BaseSentenceParser):
    
    root = bioactivity

    def interpret(self, result, start, end):

        activity = self.model(bioactivity=first(result.xpath('./text()')))

        yield activity