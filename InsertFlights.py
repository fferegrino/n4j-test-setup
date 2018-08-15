import csv
import gc
from os.path import join
import argparse
from FlightsDatabase import FlightsDatabase
from transformations import transform_as_is, transform_stringify_flights, flight_records_from_string, \
    flight_records_from_apoc, flight_records_from_maps



class InsertFlights:

    flights = []

    @staticmethod
    def load_data(location):
        if InsertFlights.flights:
            print("Nothing to load")
            return

        N = 1_000_000

        InsertFlights.flights = [None]*N

        print("Loading data flights!")
        with open(join(location, "flights_subset.csv"), "r") as csvfile:
            csvreader = csv.reader(csvfile)
            next(csvreader) # header
            i = 0
            for r in csvreader:
                flight = {
                    "airline": r[4],
                    "origin": r[7],
                    "destination": r[8],
                    "other": {
                        "tail_number": r[6],
                        "flight_number": r[5],
                        "date": {
                            "year": int(r[1]), # r["YEAR"],
                            "month": int(r[2]), # r["MONTH"],
                            "day": int(r[3]) # r["DAY"]
                        },
                        "time": {
                            "scheduled": r[17],
                            "real": r[18]
                        },
                        "flags": {
                            "weather_delay": r[11] == "1",
                            "air_system_delay": r[12] == "1",
                            "cancelled": r[9] == "1",
                            "diverted": r[10] == "1"
                        },
                        "departure": {
                            "scheduled": r[13],
                            "real": r[14]
                        },
                        "arrival": {
                            "scheduled": r[15],
                            "real": r[16]
                        }
                    }
                }
                InsertFlights.flights[i] = flight
                if i % 100_000 == 0:
                     print("Loaded", i)
                i += 1
                if i == N:
                    break
        print("Loaded %d flights" % len(InsertFlights.flights))

    # ## Using *strings*

    def insert(self, location, flights_no, instance):

        if len(InsertFlights.flights) == 0:
            InsertFlights.load_data(location)

        if instance == "3.4.0-plain":

            db_string = FlightsDatabase("bolt://localhost:7341", "neo4j", "tokyo")

            ti_strings, results_insertion_strings = db_string.insert_transform('''UNWIND {props} AS properties
                    MATCH 
                        (airline:Airline{iata:properties.airline}),
                        (departure:Airport{iata:properties.destination}),
                        (origin:Airport{iata:properties.origin})
                    CREATE (flight:Flight{
                        flight_number: properties.other.flight_number,
                        date: date(properties.other.date)
                    })
                    CREATE 
                        (flight)-[:OPERATED_BY]->(airline),
                        (flight)-[departed_from:DEPARTED_FROM]->(departure),
                        (flight)-[arrived_to:ARRIVED_TO]->(origin)
                    WITH flight, departed_from, arrived_to, properties.other as other
                    SET flight.details = other.details,
                        flight.flags = other.flags,
                        flight.departure = other.departure,
                        flight.arrival = other.arrival,
                        flight.time = other.time
                    RETURN {
                        flight_number: flight.flight_number,
                        year: flight.date.year, 
                        month: flight.date.month, 
                        day: flight.date.day,
                        flags: flight.flags,
                        arrival: flight.arrival,
                        departure: flight.departure,
                        details: flight.details,
                        time: flight.time
                    } as flight''', InsertFlights.flights[:flights_no], transform_stringify_flights)

            tr_strings, results_retrieval_string = db_string.get_maps(''' MATCH (f:Flight) 
                                    RETURN {
                                        arrival: f.arrival,
                                        date: {year: f.date.year, month: f.date.month, day: f.date.day},
                                        departure: f.departure,
                                        details: f.details,
                                        flags: f.flags,
                                        flight_number: f.flight_number,
                                        time: f.time
                                    } as flight_record''', flight_records_from_string)
                                    
            del results_retrieval_string

            db_string.close()

            return (flights_no, ti_strings, tr_strings)

        # ## Using APOC

        elif instance == "3.4.0-apoc":
            db_apoc = FlightsDatabase("bolt://localhost:7342", "neo4j", "tokyo")

            ti_apoc, results_insertion_apoc = db_apoc.insert_transform('''UNWIND {props} AS properties
                    MATCH 
                        (airline:Airline{iata:properties.airline}),
                        (departure:Airport{iata:properties.destination}),
                        (origin:Airport{iata:properties.origin})
                    CREATE (flight:Flight{
                        flight_number: properties.other.flight_number,
                        date: date(properties.other.date)
                    })
                    CREATE 
                        (flight)-[:OPERATED_BY]->(airline),
                        (flight)-[departed_from:DEPARTED_FROM]->(departure),
                        (flight)-[arrived_to:ARRIVED_TO]->(origin)
                    WITH flight, departed_from, arrived_to, properties.other as other
                    CALL apoc.convert.setJsonProperty(flight, 'details', {
                        date: flight.date, 
                        tail_number: other.tail_number
                    })
                    CALL apoc.convert.setJsonProperty(flight, 'flags', other.flags)
                    CALL apoc.convert.setJsonProperty(flight, 'departure', other.departure)
                    CALL apoc.convert.setJsonProperty(flight, 'arrival', other.arrival)
                    CALL apoc.convert.setJsonProperty(flight, 'time', other.time)
                    RETURN {
                        flight_number: flight.flight_number,
                        year: flight.date.year, 
                        month: flight.date.month, 
                        day: flight.date.day,
                        flags: flight.flags,
                        arrival: flight.arrival,
                        departure: flight.departure,
                        details: flight.details
                    } as flight''', InsertFlights.flights[:flights_no], transform_as_is)

            tr_apoc, results_retrieval_apoc = db_apoc.get_maps(''' MATCH (f:Flight) 
                                    WITH f, 
                                        apoc.convert.getJsonProperty(f, 'arrival') as arrival, 
                                        apoc.convert.getJsonProperty(f, 'departure') as departure, 
                                        apoc.convert.getJsonProperty(f, 'details') as details, 
                                        apoc.convert.getJsonProperty(f, 'flags') as flags, 
                                        apoc.convert.getJsonProperty(f, 'time') as time
                                    RETURN {
                                        arrival: arrival,
                                        date: {year: f.date.year, month: f.date.month, day: f.date.day},
                                        departure: departure,
                                        details: details,
                                        flags: flags,
                                        flight_number: f.flight_number,
                                        time: time
                                    } as flight_record''', flight_records_from_apoc)

            del results_retrieval_apoc

            db_apoc.close()

            return (flights_no, ti_apoc, tr_apoc)

        # ## Using Maps

        elif instance == "3.5.0-maps":

            db_maps = FlightsDatabase("bolt://localhost:7343", "neo4j", "tokyo")

            ti_maps, results_insertion_maps = db_maps.insert_transform('''UNWIND {props} AS properties
                    MATCH 
                        (airline:Airline{iata:properties.airline}),
                        (departure:Airport{iata:properties.destination}),
                        (origin:Airport{iata:properties.origin})
                    CREATE (flight:Flight{
                        flight_number: properties.other.flight_number,
                        date: date(properties.other.date)
                    })
                    CREATE 
                        (flight)-[:OPERATED_BY]->(airline),
                        (flight)-[departed_from:DEPARTED_FROM]->(departure),
                        (flight)-[arrived_to:ARRIVED_TO]->(origin)
                    WITH flight, departed_from, arrived_to, properties.other as other
                    SET flight.details = {
                            date: flight.date, 
                            tail_number: other.tail_number
                        },
                        flight.flags = other.flags,
                        flight.departure = other.departure,
                        flight.arrival = other.arrival,
                        flight.time = other.time
                    RETURN {
                        flight_number: flight.flight_number,
                        year: flight.date.year, 
                        month: flight.date.month, 
                        day: flight.date.day,
                        flags: flight.flags,
                        arrival: flight.arrival,
                        departure: flight.departure,
                        time: flight.time
                    } as flight''', InsertFlights.flights[:flights_no], transform_as_is)

            tr_maps, results_retrieval_maps = db_maps.get_maps(''' MATCH (f:Flight) 
                                    RETURN {
                                        arrival: f.arrival,
                                        date: {year: f.date.year, month: f.date.month, day: f.date.day},
                                        departure: f.departure,
                                        details: {
                                            tail_number: f.details.tail_number,  
                                            date: {
                                                year: f.details.date.year, 
                                                month: f.details.date.month, 
                                                day: f.details.date.day
                                            }
                                        },
                                        flags: f.flags,
                                        flight_number: f.flight_number,
                                        time: f.time
                                    } as flight_record''', flight_records_from_maps)

            del results_retrieval_maps

            db_maps.close()

            return (flights_no, ti_maps, tr_maps)
