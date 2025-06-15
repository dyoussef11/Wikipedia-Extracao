import pandas as pd
from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, ForeignKey, select, Text
import pymysql
import re
import requests
from bs4 import BeautifulSoup

tag_mapping = {
    'Beech-5': 'note 1',
    'Ohrid-6': 'note 2',
    'Jesuit-7': 'note 3',
    'Corbusier-8': 'note 4',
    'Qhapaq-9': 'note 5',
    'Ferto-10': 'note 6',
    'Alps-11': 'note 7',
    'DanubeLimes-12': 'note 8',
    'Struve-13': 'note 9',
    'Belovezhskaya-14': 'note 10',
    'Belfries-15': 'note 11',
    'Pendjari-16': 'note 12',
    'Stecci-17': 'note 13',
    'Sangha_Trinational-18': 'note 14',
    'KluaneWaterton-19': 'note 15',
    'Silk_Roads-20': 'note 16',
    'Talamanca-21': 'note 17',
    'Nimba-22': 'note 18',
    'Mining_Region-23': 'note 19',
    'Kvarken-24': 'note 20',
    'Taputapuatea-25': 'note 21',
    'Austral-26': 'note 22',
    'New_Caledonia-27': 'note 23',
    'Réunion-28': 'note 24',
    'Perdu-29': 'note 25',
    'StoneCircles-30': 'note 26',
    'Frontiers-31': 'note 27',
    'Muskauer-32': 'note 28',
    '33': 'note 29',  # Dresden Elbe Valley delisted
    'Wadden-34': 'note 30',
    'Aggtelek-35': 'note 31',
    'Rome-36': 'note 32',
    'Rhaetian-37': 'note 33',
    'Giorgio-38': 'note 34',
    'Jerusalem-39': 'note 35',
    'Tien-Shan-42': 'note 36',
    'Maloti-43': 'note 37',
    'Curonian-44': 'note 38',
    'Uvs-45': 'note 39',
    'Kathmandu_Valley-46': 'note 40',
    '47': 'note 41',  # Arabian Oryx Sanctuary delisted
    'Tserkvas-48': 'note 42',
    'Coa-49': 'note 43',
    'Mercury-50': 'note 44',
    'MosioaTunya-51': 'note 45'
}


def clean_tags(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    for i_tag in soup.find_all('i'):
        i_tag.unwrap()  # Remove a tag <i> mas mantém o texto dentro dela
    for i_tag in soup.find_all('a'):
        i_tag.unwrap()  # Remove a tag <a> mas mantém o texto dentro dela
    return str(soup)

def receber_url(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # 4. Extração das descrições das notas (reference descriptions)
    note_descriptions = {}
    # Seleciona os <li> dentro da div específica, usando select
    for li in soup.select('div.reflist-columns.references-column-width.reflist-columns-2 li'):
        # Find the reference-text span
        ref_span = li.find('span', {'class': 'reference-text'})
        tag = li.get('id', '').replace('cite_note-', '')
        
        if ref_span and tag:
            # Get the text content, preserving HTML tags within the span
            content = ''.join(str(child) for child in ref_span.contents)
            
            # Clean up the content (optional)
            content = content.replace('\n', ' ').strip()
            content = clean_tags(content)
            new_tag = tag_mapping.get(tag, tag)
            note_descriptions[new_tag] = content
    # print(f"{note_descriptions}")
    # print(f"Total descrições de notas extraídas: {len(note_descriptions)}")
    
    return note_descriptions
