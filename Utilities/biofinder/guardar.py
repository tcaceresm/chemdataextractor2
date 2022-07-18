def save_syn(drug, texto):
    '''Small script to save synonyms of chemical molecules in txt file
Parameters
----------
    
drug : string

texto: string

Creates a text file with all synonyms of drug in synonym1 | synonym2 | ... format
'''
    with open(f"./{drug}.txt", 'w') as text_file:
        text_file.write(texto)
