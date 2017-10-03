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
En este ejemplo se devuelven las fuentes de información de la API BBC Juice
'''
from juipy import *
from sys import stdout

if __name__ == '__main__':
    # Creamos el objeto para consultar a la API
    juipy = Juipy(api_key = 'KNBPaOTZgu2ASJTrmyG8G530yvtnpHKJ')

    # Las siguientes líneas muestran información de depuración de la request
    # por stdout
    logger = juipy.get_logger()
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler(stdout))

    # Obtenemos las fuentes de información
    sources = juipy.get_sources()

    # Mostramos las fuentes de información
    print('{}\n'.format('-' * 10))
    for source in sources:
        print(source)
