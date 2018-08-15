from neo4j.v1 import GraphDatabase
import sys
import time


class FlightsDatabase(object):

    def __init__(self, uri, user, password, retries=10, sleep_time=5):
        self._map_keys: set = None
        self._connected = False
        while not self._connected or retries >= 0:
            try:
                self._driver = GraphDatabase.driver(uri, auth=(user, password))
                self._connected = True
            except:
                print("Database at %s not available" % uri, file=sys.stderr)
                time.sleep(sleep_time)
            retries -= 1

    def close(self):
        self._driver.close()

    def insert(self, airlines):
        start_time = time.time()
        with self._driver.session() as session:
            tx = session.begin_transaction()
            results = tx.run('''UNWIND {props} AS properties
                                CREATE (a:Airline)
                                SET a = properties''', parameters={'props': airlines})
            tx.commit()
            tx = session.begin_transaction()
            tx.run('''CREATE INDEX ON :Airline(iata)''')
            tx.commit()

        time_elapsed = time.time() - start_time
        return time_elapsed, results

    def insert_transform(self, insert_script, properties, transform_function, indexing_script=None):
        start_time = time.time()
        transformed_properties, self._map_keys = transform_function(properties)
        with self._driver.session() as session:
            tx = session.begin_transaction()
            results = tx.run(insert_script, parameters={'props': transformed_properties})
            tx.commit()

            if indexing_script:
                tx = session.begin_transaction()
                tx.run(indexing_script)
                tx.commit()

        time_elapsed = time.time() - start_time

        return time_elapsed, results.summary().counters

    def get_maps(self, retrieve_script, transform_function):
        start_time = time.time()
        with self._driver.session() as session:
            tx = session.begin_transaction()
            results = tx.run(retrieve_script)
            tx.commit()

        result_list = transform_function(results, self._map_keys)

        time_elapsed = time.time() - start_time

        return time_elapsed, result_list

    def delete_relationships_nodes(self):
        start_time = time.time()
        with self._driver.session() as session:
            tx = session.begin_transaction()
            results = tx.run('''MATCH (o)-[r]->() DELETE o, r''')
            tx.commit()

        time_elapsed = time.time() - start_time

        return time_elapsed, results.summary().counters
