'''
Copyright (c) 2017 Víctor Ruiz Gómez

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''
'''
Este ejemplo busca los articulos usando la api BBC juice usando los siguientes
criterios:
- Se buscan solo artículos en español.
- Se menciona la palabra clave "Cataluña" y la palabra "elecciones" 
- Se han publicado en las fechas 20/9/2017 - 1/10/2017
'''

from juipy import *
from sys import stdout
from datetime import datetime

if __name__ == '__main__':
    # Creamos el objeto para consultar a la API
    juipy = Juipy(api_key = 'KNBPaOTZgu2ASJTrmyG8G530yvtnpHKJ')

    # Las siguientes líneas muestran información de depuración de la request
    # por stdout
    logger = juipy.get_logger()
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler(stdout))

    # Creamos un criterio de búsqueda
    keywords = Keyword('Cataluña') & Keyword('Elecciones')
    criteria  = SearchCriteria(keywords = keywords, lang = 'es',
                               published_before = datetime(day = 1, month = 10, year = 2017),
                               published_after = datetime(day =  20, month = 9, year = 2017))


    # Hacemos la request
    articles = juipy.search_articles(since = 0, size = 5, criteria = criteria)

    # Imprimimos los articulos obtenidos
    for article in articles:
        print('{0}\n{1}\n{0}\n'.format('-' * 10, str(article)))

