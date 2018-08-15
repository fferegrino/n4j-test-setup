# coding: utf-8

# In[1]:


import pandas as pd
import gc
import argparse
from os.path import join
from FlightsDatabase import FlightsDatabase
from transformations import transform_as_is, transform_split_maps, transform_stringify_second_level
from transformations import results_as_they_are, mapify_second_level


class InsertAirports:
    airports = []
    airlines = []

    @staticmethod
    def load_data(location):
        if InsertAirports.airlines and InsertAirports.airports:
            print("Nothing to load")
            return
        print("Loading data airport!")
        airports_csv = pd.read_csv(join(location, "airports.csv"))
        airlines_csv = pd.read_csv(join(location, "airlines.csv"))

        for _, r in airports_csv.sort_values(by='IATA_CODE').iterrows():
            a = {
                'iata': r['IATA_CODE'],
                'name': r['AIRPORT'],
                'location': {
                    'country': r['COUNTRY'],
                    'state': r['STATE'],
                    'city': r['CITY'],
                    'coordinates': {
                        'latitude': r['LATITUDE'],
                        'longitude': r['LONGITUDE']
                    }
                }
            }
            InsertAirports.airports.append(a)

        for _, r in airlines_csv.sort_values(by='IATA_CODE').iterrows():
            a = {
                'iata': r['IATA_CODE'],
                'name': r['AIRLINE']
            }
            InsertAirports.airlines.append(a)

        del airlines_csv
        del airports_csv
        gc.collect()

    def insert(self, location, instance):

        if len(InsertAirports.airlines) == 0 and len(InsertAirports.airports) == 0:
            InsertAirports.load_data(location)

        # ## Using *strings*

        if instance == "3.4.0-plain":

            db_string = FlightsDatabase("bolt://localhost:7341", "neo4j", "tokyo")

            ti_strings_airlines, _ = db_string.insert(InsertAirports.airlines)

            ti_strings, results_insertion_strings = db_string.insert_transform('''UNWIND {props} AS properties
                CREATE (a:Airport)
                SET a = properties
                RETURN a''', InsertAirports.airports, transform_stringify_second_level,
                indexing_script='''CREATE INDEX ON :Airport(iata)''')

            tr_strings, results_retrieval_strings = db_string.get_maps('''MATCH (a:Airport)
                RETURN a
                ORDER BY a.iata;''', mapify_second_level)

            db_string.close()

            return (ti_strings_airlines, ti_strings, tr_strings)

        # ## Using APOC

        elif instance == "3.4.0-apoc":

            db_apoc = FlightsDatabase("bolt://localhost:7342", "neo4j", "tokyo")

            ti_apoc_airlines, _ = db_apoc.insert(InsertAirports.airlines)

            ti_apoc, results_insertion_apoc = db_apoc.insert_transform('''UNWIND {props} AS properties
                CREATE (a:Airport)
                SET a = properties.other
                WITH a, properties
                CALL apoc.convert.setJsonProperty(a, 'location', properties.location)
                RETURN a''', InsertAirports.airports, transform_split_maps,
                indexing_script='''CREATE INDEX ON :Airport(iata)''')

            tr_apoc, results_retrieval_apoc = db_apoc.get_maps('''MATCH (airport:Airport)
                WITH apoc.convert.getJsonProperty(airport, 'location') as map, airport
                RETURN { iata: airport.iata, name: airport.name, location: map } as a
                ORDER BY airport.iata;''', results_as_they_are)

            db_apoc.close()

            return (ti_apoc_airlines, ti_apoc, tr_apoc)

        # ## Using Maps

        elif instance == "3.5.0-maps":

            db_maps = FlightsDatabase("bolt://localhost:7343", "neo4j", "tokyo")

            ti_maps_airlines, _ = db_maps.insert(InsertAirports.airlines)

            ti_maps, results_insertion_maps = db_maps.insert_transform('''UNWIND {props} AS properties
                CREATE (a:Airport)
                SET a = properties
                RETURN a''', InsertAirports.airports, transform_as_is,
                indexing_script='''CREATE INDEX ON :Airport(iata)''')

            tr_maps, results_retrieval_map = db_maps.get_maps('''MATCH (a:Airport)
                RETURN a
                ORDER BY a.iata;''', results_as_they_are)

            db_maps.close()
            
            return (ti_maps_airlines, ti_maps, tr_maps)
