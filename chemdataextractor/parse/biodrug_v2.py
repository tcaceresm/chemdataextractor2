from chemdataextractor.parse.base import BaseSentenceParser
from chemdataextractor.parse import I, join, merge, W
from chemdataextractor.utils import first

import re

'''
chemdataextractor.parse.biodrug_v2
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Drug synonyms text parser.
'''

drug_syn = open('drug_syn', 'r') #open(path/to/text_file_with_drug_synonyms, 'r')
all_syn = drug_syn.read().split('$')
drug_syn.close()



def iw_applicable(something):
    if type(something) != type(I('a') or type(something) != type(W('a'))): 
        if something in '(),{}[]':
            return W(something)
        return I(something)
    else:
        return something

def parse_whitespaces(drug_words):
    '''acetylsalicylic acid --> (I(acetilsalicylic) + I(acid)).
    As an input requires a list consisting of the words of the drug. For example,
    acetylsalicylic acid as a list ['acetylsalicylic', 'acid']'''
    
    if len(drug_words) == 2:
        return (iw_applicable(drug_words[0]) + iw_applicable(drug_words[1]))
    elif len(drug_words) == 3:
        return (iw_applicable(drug_words[0]) + iw_applicable(drug_words[1]) + iw_applicable(drug_words[2]))
    elif len(drug_words) == 4:
        return (iw_applicable(drug_words[0]) + iw_applicable(drug_words[1]) + iw_applicable(drug_words[2]) + iw_applicable(drug_words[3]))
    elif len(drug_words) == 5:
        return (iw_applicable(drug_words[0]) + iw_applicable(drug_words[1]) + iw_applicable(drug_words[2]) + iw_applicable(drug_words[3]) + iw_applicable(drug_words[4]))

def merge_elements(list_to_merge):
    '''Example: ['(', 'hydroxy', ')'] --> I('(') + I('hydroxy') + I(')')
    '''
    if len(list_to_merge) == 1:
        return (iw_applicable(list_to_merge[0]))
    else:
        element = list_to_merge.pop(0)
        return iw_applicable(element) + merge_elements(list_to_merge)

def drug_parser(drug_list):
    '''Drug list example = ['aspirine', 'acetylsalicylic acid', '2-(hydroxy)benzene']
    '''
    if len(drug_list) == 1: #Only one drug synonym in the list
        drug_name = drug_list.pop()
        if ' ' in drug_name: #This unique drug synonym has a whitespace
            drug_name_components = drug_name.split(' ')
            i = 0
            for components in drug_name_components:
                if any(x in '()-[]{},' for x in components): 
                    regex_pattern = r'(\()|(\))|(-)|(\[)|(\])|(\{)|(\})'
                    components_regex = re.split(regex_pattern, components)
                    components_regex = list(filter(None, components_regex))
                    drug_name_components[i] = merge_elements(components_regex).add_action(merge)
                    i += 1
            whitespace_done = parse_whitespaces(drug_name_components).add_action(join)
            return whitespace_done
        else: #This unique drug synonym don't have whitespace
            if any(x in '()-[]{}' for x in drug_name): #This means it has hyphen or brackets
                regex_pattern = r'(\()|(\))|(-)|(\[)|(\])|(\{)|(\})'
                components_regex = re.split(regex_pattern, drug_name)
                components_regex = list(filter(None, components_regex))                       
                components_merged = (merge_elements(components_regex)).add_action(merge)    
                return components_merged
            else:
                return I(drug_name)

    elif len(drug_list) > 1: #More than one drug in the list
        drug_name = drug_list.pop()
        if ' ' in drug_name: #The drug has a whitespace
            drug_name_components = drug_name.split(' ')
            i = 0
            for components in drug_name_components:
                if any(x in '()-[]{},' for x in components):
                    regex_pattern = r'(\()|(\))|(-)|(\[)|(\])|(\{)|(\})'
                    components_regex = re.split(regex_pattern, components)
                    components_regex = list(filter(None, components_regex))
                    drug_name_components[i] = merge_elements(components_regex).add_action(merge)
                    i += 1
            whitespace_done = parse_whitespaces(drug_name_components).add_action(join)
            return whitespace_done | drug_parser(drug_list)
        else: #The drug don't have a whitespace
            if any(x in '()-[]{},' for x in drug_name):
                regex_pattern = r'(\()|(\))|(-)|(\[)|(\])|(\{)|(\})'
                components_regex = re.split(regex_pattern, drug_name)
                components_list = list(filter(None, components_regex))
                components_merged = merge_elements(components_list).add_action(merge)    
                return components_merged | drug_parser(drug_list)
            else:
                return I(drug_name) | drug_parser(drug_list)
            #tiene que terminar con un join

drug = drug_parser(all_syn)
drug_phrase = (drug)('dg')

class DrugParser(BaseSentenceParser):
    
    root = drug_phrase

    def interpret(self, result, start, end):

        activity = self.model(drug=first(result.xpath('./text()')))

        yield activity