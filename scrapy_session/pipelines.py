# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import scrapy
from itemadapter import ItemAdapter
import json
import os


class ScrapySessionPipeline:
    def process_item(self, item, spider):
        return item


class QuotesPipeline:
    def __init__(self):
        self.quotes_seen = set()

    def process_item(self, item, spider):
        # Paso 1: Filtrar citas duplicadas
        print("Dirty: ", item)
        if item['quote'] in self.quotes_seen:
            raise scrapy.exceptions.DropItem(f"Cita duplicada encontrada: {item['quote']}")
        self.quotes_seen.add(item['quote'])

        # Paso 2: Limpiar datos
        item['quote'] = item['quote'].strip().replace("“", "").replace("”", "")
        item['author'] = item['author'].strip()
        print("Clean: ", item)
        # Retornar el item limpio
        return item

    def close_spider(self, spider):
        print("Pipeline finalizado. Citas únicas procesadas:", len(self.quotes_seen))


class QuotesByTagPipeline:
    def open_spider(self, spider):
        # Crear el directorio "quotes_by_tag" si no existe
        self.directory = 'quotes_by_tag'
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)
        # Inicializar un diccionario para abrir múltiples archivos por etiqueta
        self.files = {}

    def process_item(self, item, spider):
        for tag in item['tags']:
            file_path = os.path.join(self.directory, f"{tag}.json")

            # Abre el archivo en modo 'append' y guarda la referencia
            if tag not in self.files:
                self.files[tag] = open(file_path, 'a')

            # Escribir el item en el archivo correspondiente
            line = json.dumps({
                'quote': item['quote'],
                'author': item['author']
            }) + "\n"
            self.files[tag].write(line)

        return item

    def close_spider(self, spider):
        # Cerrar todos los archivos abiertos
        for file in self.files.values():
            file.close()
        print("Pipeline de clasificación completado. Archivos generados por etiqueta.")
