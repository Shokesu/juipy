Esta pequeña librería es un wrapper en python sobre la API BBC Juicer, la cual es útil para consultar información de artículos y
publicaciones de distintas fuentes.

# Instalación
Para usar esta librería, necesitarás la versión python 3.5 o posterior.
Son necesarias las siguientes dependencias: urllib3, pyvalid, requests

# Introducción
Como ejemplo demostrativo, este código imprime información de artículos publicados por los periódicos digitales
"El Pais" y "La Vanguardia Digital" que hagan referencia al cambio climático, en el cuerpo del artículo o en el título.
Reemplaza {{api_key}} por tu API key de BBC Juicer

```
from juipy import *

if __name__ == '__main__':
    # Creamos el objeto para consultar a la API
    juipy = Juipy(api_key = '{{api_key}}')
    
    # Creamos un criterio de búsqueda
    criteria  = SearchCriteria(keywords = 'cambio climático', sources = ['La Vanguardia Digital', 'El Pais'])

    # Realizamos la búsqueda
    articles = juipy.search_articles(since = 0, size = 5, criteria = criteria)

    # Imprimimos los articulos obtenidos
    for article in articles:
        print('{0}\n{1}\n{0}\n'.format('-' * 10, str(article)))
```

Este ejemplo y otros más están disponibles en https://github.com/Shokesu/juipy/tree/master/test
