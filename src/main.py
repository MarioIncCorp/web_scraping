import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import matplotlib.pyplot as plt
import logging

# Configuración del archivo de log
logging.basicConfig(
    filename="scraping.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def web_scraping( num_paginas):
    # URL del sitio al que se le hará scraping
    base_url = "http://books.toscrape.com/catalogue/page-{}.html"

    libros = []

    # Headers para evitar bloqueos. Originalmente 
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X)"
    }

    # La lectura de las páginas se hace con ayuda del ciclo for y la función range, 
    # usada para crear un rango del primer elemento al último menos uno
    for pagina in range(1, num_paginas + 1):

        # Como la variable base_url es de tipo string, se puede usar el método format
        # para hacer una sustitución del número de la página por la etiqueta {} 
        url = base_url.format(pagina)

        # Se utiliza try catch para control de excepciones
        try:
            # Usando el método get del objeto request se carga la información en la varible response
            response = requests.get(url, headers=headers)

            # Se revisa el código HTTP de la respuesta
            response.raise_for_status()

            # Con la función BeautifulSoup se extrae el texto de la página con formato html
            soup = BeautifulSoup(response.text, "html.parser")

            # Dentro del ciclo se buscan los elementos article con la clase de css
            # product_pod
            for libro in soup.find_all("article", class_="product_pod"):

                ## Se obtiene el título del libro en base a la etiqueta de tipo h3
                ## y el elemento title
                titulo = libro.h3.a["title"]

                ## Se obtiene el precio del libro dentro de la etiqueta p
                ## y con la clase css price_color
                precio_fstring = libro.find("p", class_="price_color").text

                ## Limpiamos el formato del precio (£51.77 -> 51.77)
                ## El precio tiene un formato moneda (dado en libras)
                ## Se quita el signo de libras £
                #print(precio_fstring)
                precio_fstring = precio_fstring.replace("Â", "")
                precio_fstring = precio_fstring.replace("£", "")
                precio = float(precio_fstring)

                ## Se leé la disponibilidad del libro
                ## basados en la etiqueta p con las clases css instock availability
                disponibilidad = libro.find("p", class_="instock availability").text.strip()

                ## Se obtiene la clasificación en base la etiqueta p con las clase css
                ## star-rating en la primera coincidencia
                rango = libro.find("p", class_="star-rating")["class"][1]
                rango_str = ""
                #print("Rango: ", rango)
                match rango:
                    case "One":
                        rango_str = "Primero"
                    case "Two":
                        rango_str = "Segundo"
                    case "Three":
                        rango_str = "Tercero"
                    case "Four":
                        rango_str = "Cuarto"
                    case "Five":
                        rango_str = "Quinto"
                    case _:
                        rango_str = "Sin Mapear"
                ## El resultado se guarda en la lista boks
                libros.append({
                    "Título": titulo,
                    "Precio": precio,
                    "Disponibilidad": disponibilidad,
                    "Rango": rango_str
                })

            # Se imprime mensaje de lectura completada
            print(f"La página {pagina} ha sido procesada")

            # Como medida de prevensión para no saturar el servidor
            # se tiene un periodo de espera antes de continuard con la siguiente página
            time.sleep(random.uniform(1, 3))

        except requests.exceptions.RequestException as e:
            # Las excepciones de tipo RequestException se "atrapan" en esta sección y se guardan en un archivo log
            print("Error en la página", pagina, e)
            logging.error(f"Error de conexión en la página {pagina}: {e}")
        except Exception as ex:
            print("Se presentó una excepción al analizar la página" , pagina, ex)
            logging.exception(f"Error al analizar la página {pagina}: {ex}")

    # Con la información recopilada se crea una DataFrame que servirá
    # para generar un documento CSV
    df = pd.DataFrame(libros)

    # Guardar CSV
    df.to_csv("libros_multiple_pages.csv", index=False)

    print("Total de libros analizados:", len(df))

    # En terminal se imprime una tabla con el resultado
    print(df.head())

    return df

def limpieza_datos(raw_data):
    mapa_rangos = {
        "Primero":1,
        "Segundo":2,
        "Tercero":3,
        "Cuarto":4,
        "Quinto":5
    }

    #Se agrega una nueva columna, mapeando la columna rango para establecer su equivalencia en número
    raw_data["rango_num"] = raw_data["Rango"].map(mapa_rangos)

    return raw_data

def grafica_distribucion_precios(libros):
    ## Se construye una gráfica para mostrar la distribución de libros por precio
    ## Lo que muestra dónde se concentran los mayores costos
    plt.figure(figsize=(10,6))

    # Especifica histograma sobre precio del libro
    plt.hist(libros["Precio"], bins=30)

    # Título de la gráfica
    plt.title("Distribución de precios de libros")

    # Título del eje X
    plt.xlabel("Precio (£)")

    # Título del eje Y   
    plt.ylabel("Cantidad de libros")

    # Se grafica la información
    plt.grid(True)
    plt.show()


def grafica_precio_promedio_x_rango(libros):

    # Agrupa los libros por rango/rating y precio
    avg_price_rating = libros.groupby("rango_num")["Precio"].mean()

    # Se gestiona el espacio de la gráfica
    plt.figure(figsize=(8,5))

    # Se establece el tipo de gráfica
    avg_price_rating.plot(kind="bar")

    # Título de la gráfica
    plt.title("Precio promedio por calificación (rango)")

    # Título del eje X
    plt.xlabel("Calificación")

    # Título del eje Y
    plt.ylabel("Precio promedio (£)")

    # Se grafica la información
    plt.xticks(rotation=0)
    plt.grid(axis='y')

    plt.show()

def libros_x_rango(libros):
    ## Ordena los libros sobre la columna de rango/rating de tipo numérico
    rating_count = libros["rango_num"].value_counts().sort_index()

    # Se prepara el esquema de graficación
    plt.figure(figsize=(8,5))

    # Se establece el tipo de gráfica
    rating_count.plot(kind="bar")

    # Título de la gráfica
    plt.title("Cantidad de libros por calificación (rango)")

    # Titulo del eje x
    plt.xlabel("Rango")

    # Título del eje y
    plt.ylabel("Número de libros")

    plt.grid(axis='y')
    plt.show()


if __name__ == '__main__':
   # Número de páginas a leer. El sitio presenta la información por páginas
   # por eso se toma una muestra de las diez páginas iniciales
   # El número máximo de páginas es 50
   raw_data = web_scraping(2)

   # Agrega una columna númerica para correlacionar con el rango
   new_data = limpieza_datos(raw_data)

   grafica_distribucion_precios(new_data)

   # Se busca identificar los libros mejor calificados y que tienden a ser más caros.
   grafica_precio_promedio_x_rango(new_data)

   # Aquí se grafica distribución de calidad del catálogo.
   libros_x_rango(new_data)