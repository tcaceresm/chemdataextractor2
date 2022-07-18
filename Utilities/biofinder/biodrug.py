from chemdataextractor.parse.base import BaseSentenceParser
from chemdataextractor.parse import I, join, merge, W
from chemdataextractor.utils import first

import re

'''
chemdataextractor.parse.biodrug_v2
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Drug synonyms text parser.
'''

## 

drug_syn = open(r'D:\UC\biofinder\aspirin.txt', 'r') #open(path/to/text_file_with_drug_synonyms, 'r')
all_syn = drug_syn.read().split('$')
drug_syn.close()





def iw_applicable(word):
    '''
    Aplica la funcion I() o W() cuando corresponde.
    Recibe una palabra o parentesis
    '''
    if not isinstance(word, (type(W('a')), type(I('a')), type((I('a') + I('a'))))): 
        if word in '()}{[]-':
            return W(word)
        return I(word)
    else:
        return word



def parse_whitespaces(drug_words):
    '''acetylsalicylic acid --> (I(acetilsalicylic) + I(acid)).
    As an input requires a list consisting of the words of the drug. For example,
    acetylsalicylic acid as a list ['acetylsalicylic', 'acid']
    
    Si un sinónimo está compuesto de más de 6 palabras, el programa se caera.
    
    '''

    if len(drug_words) == 2:
        return (iw_applicable(drug_words[0]) + iw_applicable(drug_words[1]))
    elif len(drug_words) == 3:
        return (iw_applicable(drug_words[0]) + iw_applicable(drug_words[1]) + iw_applicable(drug_words[2]))
    elif len(drug_words) == 4:
        return (iw_applicable(drug_words[0]) + iw_applicable(drug_words[1]) + iw_applicable(drug_words[2]) + iw_applicable(drug_words[3]))
    elif len(drug_words) == 5:
        return (iw_applicable(drug_words[0]) + iw_applicable(drug_words[1]) + iw_applicable(drug_words[2]) + iw_applicable(drug_words[3]) + iw_applicable(drug_words[4]))
    elif len(drug_words) == 6:
        return (iw_applicable(drug_words[0]) + iw_applicable(drug_words[1]) + iw_applicable(drug_words[2]) + iw_applicable(drug_words[3]) + iw_applicable(drug_words[4]) + iw_applicable(drug_words[5]))


def merge_elements(list_to_merge):
    '''
    Recibe una lista de los elementos a los que hay que aplicar la funcion I() o W()
    Example: ['(', 'hydroxy', ')'] --> I('(') + I('hydroxy') + I(')')
    '''
    if len(list_to_merge) == 1:
        return (iw_applicable(list_to_merge[0]))
    else:
        element = list_to_merge.pop(0)
        return iw_applicable(element) + merge_elements(list_to_merge)

def drug_parser(drug_list):
    '''
    La idea de esta funcion recursiva es escribir las reglas gramaticales para encontrar cualquiera 
    de las menciones de los sinonimos de una droga. Para ello debemos analizar todos los sinonimos de la droga:

    Para aspirine --> I('aspirine) #hace match con la palabra aspirine, case insensitive
    Para acetylsalicylic acid --> I('acetylsalicylic) + I('acid).add_action(join) #match con acetylsalycilic acid

    Como input recibe una lista con los nombres de los sinonimos de la droga   ['syn1', 'syn2'].
    Retorna el parser

    '''

    if len(drug_list) == 1 and drug_list[0] == '':
        raise ValueError('Lista de sinonimos vacia')


    if len(drug_list) == 1:  #Caso base, cuando queda el último sinónimo
 
        drug_name = drug_list.pop(0) #obtengo uno de los sinónimos

        if ' ' in drug_name: #Evalua si el sinonimo tiene espacio
            #Ej. Hydroxy benzene

            drug_name_components = drug_name.split(' ')

            if len(drug_name_components) <= 6:

                #La variable drug name components es una lista que contiene todas las palabras del sinonimo
                
                #Cada palabra del sinonimo se define en base a si esta separada por un espacio.
                #Por ejemplo, paracetamol esta compuesta de una palabra y Acido acetico esta compuesta de dos palabras

                i = 0
                for components in drug_name_components:
                    #la variable componentes hace referencia a cada palabra que forma parte  del sinonimo

                    if any(x in '()-[]}{' for x in components): 

                        #Para chequear si la palabra tiene parentesis o guión. 3-(hydroxy) --> TRUE
                        #Lo que se quiere hacer es separar en base a los parentesis o guiones. ['3', '-', '(', 'hydroxy', ')']

                        regex_pattern = r'(\()|(\))|(-)|(\[)|(\])|(\{)|(\})'
                        components_splitted = re.split(regex_pattern, components)                
                        components_splitted = list(filter(None, components_splitted))

                        #Finalmente, aplico la funcion merge_elements a cada elemento obtenido
                        drug_name_components[i] = merge_elements(components_splitted).add_action(merge)

                        i += 1 #Continuo a la siguiente palabra o componente del sinonimo.

                whitespace_done = parse_whitespaces(drug_name_components) #.add_action(join)
                return whitespace_done
            else:
                print(f'El sinonimo "{drug_name}" posee mas de 6 palabras y no sera utilizado')
                return I('')

        else: #This unique drug synonym don't have whitespace
            if any(x in '()-[]}{' for x in drug_name): #This means it has hyphen or brackets
                regex_pattern = r'(\()|(\))|(-)|(\[)|(\])|(\{)|(\})'
                components_regex = re.split(regex_pattern, drug_name)
                components_regex = list(filter(None, components_regex))                       
                components_merged = (merge_elements(components_regex)).add_action(merge)    
                return components_merged
            else:
                return I(drug_name)

    elif len(drug_list) > 1: #Existe mas de un sinónimo de la droga

        drug_name = drug_list.pop(0)

        if ' ' in drug_name: #The drug has a whitespace

            drug_name_components = drug_name.split(' ')

            if len(drug_name_components) > 6:
                print(f'El sinonimo "{drug_name}" contiene mas de 6 palabras y no sera utilizado')

                return drug_parser(drug_list)
            
            else:
                i = 0
                for components in drug_name_components:
                    if any(x in '()-[]}{' for x in components):
                        regex_pattern = r'(\()|(\))|(-)|(\[)|(\])|(\{)|(\})'
                        components_regex = re.split(regex_pattern, components)
                        components_regex = list(filter(None, components_regex))

                        drug_name_components[i] = merge_elements(components_regex).add_action(merge)
                        i += 1
                        
                whitespace_done = parse_whitespaces(drug_name_components).add_action(join)
                
                return whitespace_done | drug_parser(drug_list)

        else: #The drug don't have a whitespace
            if any(x in '()-[]}{' for x in drug_name):
                regex_pattern = r'(\()|(\))|(-)|(\[)|(\])|(\{)|(\})'
                components_regex = re.split(regex_pattern, drug_name)
                components_list = list(filter(None, components_regex))
                components_merged = merge_elements(components_list).add_action(merge)    
                return components_merged | drug_parser(drug_list)
            else:
                
                return I(drug_name) | drug_parser(drug_list)
            #tiene que terminar con un join


drug = drug_parser(all_syn)

# if drug == None:
#     raise ValueError
drug_phrase = (drug)('dg')

class DrugParser(BaseSentenceParser):
    
    root = drug_phrase

    def interpret(self, result, start, end):

        activity = self.model(drug=first(result.xpath('./text()')))

        yield activity