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
import requests
import logging
import json
from urllib.parse import urlencode
from datetime import datetime
from functools import reduce
from pyvalid import accepts
from pyvalid.validators import is_validator
from re import match, fullmatch
from copy import copy
from os.path import dirname, join



class Keyword:
    '''
    Representa una palabra clave o keyword
    '''
    @accepts(object, str)
    def __init__(self, name):
        '''
        Inicializa la instancia.
        :param name: Es la palabra clave, un string
        '''
        self.name = name

    def __str__(self):
        return self.name

    def __or__(self, other):
        return KeywordsFormula.__OR__(self, other)

    def __and__(self, other):
        return KeywordsFormula.__AND__(self, other)


class KeywordsFormula:
    '''
    Representa una fórmula que consta de un conjunto de claves o keywords
    unidas entre si por operadores lógicos AND y OR
    '''
    @accepts(object, object, str, object)
    def __init__(self, clauseA, op, clauseB):
        '''
        Inicializa la instancia.
        :param clauseA Debe ser una instancia de la clase Keyword u otra instancia de
        la clase KeywordsFormula
        :param op Es el operador que une las clausulas que se indican como parámetro, 'or' o 'and'
        :param clauseB Debe ser una instancia de la clase Keyword u otra instancia de la
        clase KeywordsFormula
        Por defecto, se cons
        '''
        self.clauseA = clauseA
        self.clauseB = clauseB
        self.op = op


    def __str__(self):
        return '{} {} {}'.format(
            '({})'.format(str(self.clauseA)) if isinstance(self.clauseA, KeywordsFormula) else str(self.clauseA),
            self.op.upper(),
            '({})'.format(str(self.clauseB)) if isinstance(self.clauseB, KeywordsFormula) else str(self.clauseB))

    def __or__(self, other):
        return self.__OR__(self, other)

    def __and__(self, other):
        return self.__AND__(self, other)

    @staticmethod
    @accepts(object, object)
    def __OR__(A, B):
        if not isinstance(A, (Keyword, KeywordsFormula)) or not isinstance(B, (Keyword, KeywordsFormula)):
            raise ValueError()
        return KeywordsFormula(A, 'or', B)

    @staticmethod
    @accepts(object, object)
    def __AND__(A, B):
        if not isinstance(A, (Keyword, KeywordsFormula)) or not isinstance(B, (Keyword, KeywordsFormula)):
            raise ValueError()
        return KeywordsFormula(A, 'and', B)





class SearchCriteria:
    '''
    Esta clase representa un criterio de búsqueda para consultar articulos en la API Juicy

    '''
    dbpedia_root_url = 'http://dbpedia.org/page'

    class Validator:
        '''
        Esta clase se encarga de válidar algunos parámetros de los métodos de la clase
        SearchCriteria
        '''
        @staticmethod
        @is_validator
        def _validate_keywords(keywords):
            '''
            Este método valida el campo "keywords"
            :param keywords:
            :return:
            '''
            if keywords is None or isinstance(keywords, (str, Keyword, KeywordsFormula)):
                return True
            if isinstance(keywords, list) and len([keyword for keyword in keywords if not isinstance(keyword, (str, Keyword, KeywordsFormula))]) == 0:
                return True
            return False

        @staticmethod
        @is_validator
        def _validate_sources(sources):
            '''
            Este método valida el campo "sources"
            :param sources:
            :return:
            '''
            if sources is None or isinstance(sources, (str, int)):
                return True

            if isinstance(sources, list) and len([source for source in sources if not isinstance(source, (str, int))]) == 0:
                return True
            return False

        @staticmethod
        @is_validator
        def _validate_facets(facets):
            '''
            Este método valida el campo "facets"
            :param facets:
            :return:
            '''
            if facets is None or isinstance(facets, str):
                return True
            if isinstance(facets, list) and len([facet for facet in facets if not isinstance(facet, str)]) == 0:
                return True
            return False

        @staticmethod
        @is_validator
        def _validate_like_ids(like_ids):
            '''
            Este método valida el campo "like_ids"
            :param like_ids:
            :return:
            '''
            if like_ids is None or isinstance(like_ids, int):
                return True
            if isinstance(like_ids, list) and len([id for id in like_ids if not isinstance(id, int)]) == 0:
                return True
            return False

        @staticmethod
        @is_validator
        def _validate_date(date):
            '''
            Este método válida una fecha
            :param date:
            :return:
            '''
            if date is None or isinstance(date, datetime):
                return True
            if isinstance(date, str):
                try:
                    datetime.utcfromtimestamp(float(date))
                    return True
                except:
                    pass
            return False


    @accepts(object, keywords = Validator._validate_keywords, lang = ('es', 'en'),
             published_before = Validator._validate_date, published_after = Validator._validate_date,
             sources = Validator._validate_sources, facets = Validator._validate_facets,
             like_text = str, like_ids = Validator._validate_like_ids)
    def __init__(self, keywords = None, lang = None, published_before = None,
                 published_after = None, sources = None, facets = None,
                 like_text = None, like_ids = None):
        '''
        Inicializa la instancia
        :param keywords: Indica palabras clave que se buscarán en el título, descripción o
        cuerpo de cada articulo.
        Cada keyword puede ser un string o una instancia de la clase Keywords.
        Puede especificarse varios (con una lista)

        e.g:
        keywords = 'Barack Obama'
        keywords = ['Barack Obama', 'Donald Trump']

        También puede ser una fórmula de este estilo:
        keywords = (Keyword('Barack Obama') & (Keyword('Donald Trump')) | Keyword('climatic change'))

        :param lang: Establece el lenguaje de los articulos a consultar. Puede ser un string
        e.g: lang = 'es'
        Por el momento, solo los lenguajes 'es' y 'en' están disponibles.

        :param published_before: Si se especifica, se obtendrán articulos cuya fecha de publicación
        es posterior a esta. Puede ser un string o entero, en cuyo caso se interpretará que es un
        timestamp de POSIX. En caso contrario, debe ser una instancia de la clase datetime.datetime
        Este fecha debe ser UTC.

        :param published_after: Es igual que el parámetro anterior, solo que indica la fecha más
        reciente que puede tener un articulo.

        :param sources: Indica sobre que fuentes de información deben buscarse los articulos.
        Puede se un string/int o una lista de strings/ints, que indicarán una fuente de información o varias
        de ellas respectivamente.
        Puede especificarse cada fuente por nombre, en cuyo caso debe ser un string, o por ID
        (entero)
        e.g:
        sources = 'Birmingham Post'
        sources = ['Birmingham Post', 'Irish Independent', 26]


        :param facets: Indica una o varias entidades. Se obtendrán los articulos que se hagan
        referencia a una o varias de estas entidades.
        Los facets son entidades de DBPedia.
        e.g, por ejemplo, si se indica la entidad 'Barack_Obama', se pasará como parámetro a la
        request de Juicy, el facet 'http://dbpedia.org/page/Barack_Obama'

        :param like_text: Es un texto en forma de string. Si se indica, se buscarán articulos cuyo
        contenido sea parecido a este texto.

        :param like_ids: Es una ID (entero) o una lista de enteros. Si se indica, se buscarán
        articulos cuyo contenido es similiar al/los articulo(s) cuyas IDs se indican como
        parámetro.
        '''

        self.keywords = keywords
        self.lang = lang


        to_date = lambda time:datetime.utcfromtimestamp(float(time)) if not isinstance(time, datetime) else time
        self.published_before = to_date(published_before) if not published_before is None else None
        self.published_after = to_date(published_after) if not published_after is None else None

        self.sources = sources
        self.facets = facets
        self.like_text = like_text
        self.like_ids = like_ids



    def _parse(self):
        '''
        Parsea el criterio de búsqueda y lo convierte en un diccionario que posteriormente será
        codificado en la url de la request.
        '''

        params = {}

        # Parámetros para búsqueda por keywords
        if not self.keywords is None:
            if isinstance(self.keywords, str):
                params['q'] = self.keywords
            elif isinstance(self.keywords, list):
                if len(self.keywords) > 0:
                    keywords = reduce(lambda x,y: x & y,
                           [keyword for keyword in self.keywords if isinstance(keyword, (Keyword, KeywordsFormula))] +\
                           [Keyword(keyword) for keyword in self.keywords if isinstance(keyword, str)])
                    params['q'] = str(keywords)
                else:
                    pass
            elif isinstance(self.keywords, (Keyword, KeywordsFormula)):
                params['q'] = str(self.keywords)


        # Parámetro para búsqueda por lenguaje
        if not self.lang is None:
            params['lang'] = self.lang

        # Parámetros para búsqueda por fecha de publicación
        formatted_date = lambda date:'{}Z'.format(date.isoformat('T'))
        if not self.published_before is None:
            params['published_before'] = formatted_date(self.published_before)

        if not self.published_after is None:
            params['published_after'] = formatted_date(self.published_after)

        # Parámetro para búsqueda por fuentes de información.
        if not self.sources is None:
            params['sources[]'] = self.sources

        # Parámetro para búsqueda por facets
        if not self.facets is None:
            formatted_facet = lambda facet:'{}/{}'.format(self.dbpedia_root_url, facet)
            if isinstance(self.sources, list):
                params['facets[]'] = [formatted_facet(facet) for facet in self.facets]
            else:
                params['facets[]'] = formatted_facet(self.facets)

        # Más parámetros...
        if not self.like_text is None:
            params['like-text'] = self.like_text

        if not self.like_ids is None:
            pass

        return params




class Article:
    '''
    Esta clase proporciona información relevante de los articulos
    devueltos por la API BBC Juice
    '''
    @accepts(object, int, str, datetime)
    def __init__(self, id, url, published_at):
        self.id = id
        self.url = url
        self.published_at = published_at

    def get_id(self):
        '''

        :return: Devuelve la ID del articulo en la API BBC Juice
        '''
        return self.id


    def get_url(self):
        '''

        :return: Devuelve la url del articulo.
        '''
        return self.url

    def get_published_at(self):
        '''

        :return: Devuelve una instancia de la clase datetime, que indica la fecha
        en la que se publicó o se vió por primera vez el artículo.
        '''
        return self.published_at

    def get_domain(self):
        '''

        :return: Devuelve el dominio de la url donde se publicó el articulo
        '''
        result = fullmatch(pattern = 'https?\:\/\/([^\/]+).*', string = self.get_url())
        domain = result.group(1)
        return domain

    def __str__(self):
        s = 'Articulo publicado en {}\n'.format(self.get_domain())
        s += '{}\n'.format(self.get_url())
        s += 'Publicado en {} con id = {}'.format(str(self.get_published_at()), str(self.get_id()))
        return s


class Source:
    '''
    Representa una fuente de información desde donde BBC Juice extrae y consulta
    articulos
    '''
    def __init__(self, id, name):
        self.id = id
        self.name = name

    def get_id(self):
        '''

        :return: Devuelve la ID de la fuente
        '''
        return self.id

    def get_name(self):
        '''
        :return: Devuelve el nombre de la fuente
        '''
        return self.name

    def __str__(self):
        return self.get_name()


class Juipy:
    '''
    Esta clase permite obtener información de articulos, canales de TV y otras fuentes
    de información usando la api BBC Juicer
    '''

    root_url = 'http://juicer.api.bbci.co.uk'


    @accepts(object, api_key = str)
    def __init__(self, api_key):
        '''
        Inicializa la instancia.
        :param api_key: Debe ser la clave para la API BBC Juicer que usará para realizar
        las requests.
        '''
        self.api_key = api_key

        # Logger para mostrar información de depuración
        self.logger = logging.getLogger(__name__)

        # Información sobre las fuentes de información de BBC Juice
        self.sources = None

    def get_logger(self):
        '''
        :return: Devuelve el objeto que es usado para mostrar información de depuración
        de las requests
        '''
        return self.logger


    @accepts(object, size = int, since = int, criteria = SearchCriteria)
    def search_articles(self, size = 10, since = 0, criteria = None, timeout = None, *args, **kwargs):
        '''
        Busca articulos publicados en distintas fuentes.
        :size Es el número de articulos a devolver. Por defecto, 10
        :since Es una id que indica el offset del primer articulo a devolver en el resultado.
        Por defecto, 0
        Puede ser usado junto con el parámetro size para paginar los articulos.
        :param criteria: Debe ser una instancia de la clase SearchCriteria. Indicará
        el criterio de búsqueda.
        Si es None, se podrán especificar los mismos parámetros que los que se utilizan para
        inicializar una instancia de la clase SearchCriteria.
        :param timeout: Será el timeout de la request, por defecto no habrá timeout.
        Si se produce cualquier error al realizar la request, se genera una excepción
        '''
        try:
            if criteria is None:
                criteria = SearchCriteria(*args, **kwargs)

            # Que parámetros pasaremos a la query
            params = criteria._parse()
            params.update({'size' : size, 'since' : 0})

            # El parámetro sources[] solo puede tener IDs y no nombres.
            # Realizamos una conversión...
            if ('sources[]' in params) and\
                    (isinstance(params['sources[]'], str) or len([source for source in params['sources[]'] if isinstance(source, str)]) > 0):
                if self.sources is None:
                    try:
                        self.sources = self.get_sources(timeout = 10)
                    except:
                        raise Exception('Failed to fetch source info data')

                try:
                    def get_source_id_by_name(name):
                        return [source.get_id() for source in self.sources if source.get_name() == name][0]

                    names = params['sources[]']
                    if isinstance(names, str):
                        ids = get_source_id_by_name(names)
                    else:
                        ids = [get_source_id_by_name(name) for name in names]

                    params['sources[]'] = ids
                except:
                    raise Exception('Failed to translate source names to IDs')


            # Hacemos la request
            result = self._request('articles', params, timeout)

            try:
                articles = self._parse_articles_from_response(result)
                return articles
            except:
                raise Exception('Failed to extract article data from JSON response')
        except Exception as e:
            raise Exception('Request to BBC juice ({}) failed: {}'.format('articles', *e.args))


    def get_sources(self, timeout = None):
        '''
        Consulta las fuentes de información de la API BBC Juice
        :param timeout: Será el timeout de la request, por defecto no habrá timeout.
        :return: Devuelve una lista de todas las fuentes de información de BBC
        Juice (una lista con instancias de la clase Source)
        '''
        try:
            #result = self._request('sources', timeout = timeout)
            with open(join(dirname(__file__), 'data', 'sources.json'), 'r') as sources_file_handler:
                result = json.loads(sources_file_handler.read())
            try:
                sources = self._parse_sources_from_response(result)
                return sources
            except:
                raise Exception('Failed to extract source info data from JSON response')
        except Exception as e:
            raise Exception('Request to BBC juice ({}) failed: {}'.format('sources', *e.args))


    def _request(self, endpoint, params = {}, timeout = None):
        '''
        Lanza una request sobre la API de BBC Juice.
        :param params: Son los parámetros de la request, en forma de diccionario
        (no se necesario especificar la clave API)
        :return: Devuelve el cuerpo de la respuesta codificado en JSON
        '''
        params = copy(params)

        # Especificamos también la API key
        params['api_key'] = self.api_key

        # Replicamos parámetros duplicados en la url
        params = reduce(lambda l, x: l + [x] if not isinstance(x[1], list) else \
            l + [(x[0], value) for value in x[1]],
                        [(key, value) for key, value in params.items()], [])

        # Construimos la query
        query = '{}/{}?{}'.format(self.root_url, endpoint, urlencode(params))
        self.logger.debug('URL encoded: {}'.format(query))

        # Hacemos la request
        response = requests.get(query, timeout = timeout)

        # Comprobamos que la respuesta tiene código 200
        self.logger.debug('Response status code: {}'.format(response.status_code))
        self.logger.debug('Response headers: {}'.format(response.headers))

        if response.status_code != 200:
            raise Exception('Server response with {}'.format(response.status_code))

        try:
            result = response.json()
            return result
        except:
            raise Exception('Failed to decode response to JSON')


    @staticmethod
    def _parse_articles_from_response(response):
        '''
        Este método extrae información de artículos de la respuesta a una request a la API
        BBC Juice en formato JSON
        :param response:
        :return:
        '''
        def parse_article(data):
            url = data['url']
            id = int(data['id'])
            published_at = datetime.strptime(data['first_published_or_seen_at'], '%Y-%m-%dT%H:%M:%S.%fZ')
            article = Article(id, url, published_at)

            return article

        hits = response['hits']
        articles = []
        for hit in hits:
            try:
                article = parse_article(hit)
                articles.append(article)
            except Exception as e:
                print(e)

        return articles

    @staticmethod
    def _parse_sources_from_response(response):
        '''
        Este método extra información de fuentes de información del cuerpo de la respuesta a una request
        de la API BBC Juice codificada en formato JSON
        :param response:
        :return:
        '''
        def parse_source(data):
            id = int(data['id'])
            name = data['name']
            source = Source(id, name)
            return source

        sources = []
        for data in response:
            try:
                source = parse_source(data)
                sources.append(source)
            except:
                pass
        return sources