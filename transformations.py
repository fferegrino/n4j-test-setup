import json
from neo4j.v1.result import BoltStatementResult as BoltStatementResult


def transform_stringify_second_level(array_of_dicts: list):
    array = []
    dict_keys = set()
    for a in array_of_dicts:
        aa = {}
        for k in a:
            if type(a[k]) == dict:
                dict_keys.add(k)
                aa[k] = json.dumps(a[k])
            else:
                aa[k] = a[k]
        array.append(aa)
    return array, dict_keys


def transform_stringify_flights(flights_):
    fs = []
    for f in flights_:
        date = f["other"]["date"]
        new_flight = {
            'airline': f["airline"],
            'origin': f["origin"],
            'destination': f["destination"],
            'other': {
                'flight_number': f["other"]["flight_number"],
                'date': '%4d-%02d-%02d' % (date["year"], date["month"], date["day"]),
                'details': json.dumps({
                    'date': '%4d-%02d-%02d' % (date["year"], date["month"], date["day"]),
                    'tail_number': f["other"]["tail_number"]
                }),
                'time': json.dumps(f["other"]["time"]),
                'flags': json.dumps(f["other"]["flags"]),
                'departure': json.dumps(f["other"]["departure"]),
                'arrival': json.dumps(f["other"]["arrival"])
            }
        }
        fs.append(new_flight)
    return fs, None


def transform_split_maps(array_of_dicts: list):
    array = []
    map_keys = set()
    for a in array_of_dicts:
        aa = {}
        maps = []
        for k in a:
            if type(a[k]) == dict:
                map_keys.add(k)
                maps.append((k, a[k]))
            else:
                aa[k] = a[k]
        obj = {'other': aa}
        for k, map_ in maps:
            obj[k] = map_
        array.append(obj)
    return array, map_keys


def transform_as_is(array_of_dicts: list):
    return array_of_dicts, None


def results_as_they_are(result: BoltStatementResult, keys: set):
    return [dict(r['a'].items()) for r in result.records()]


def mapify_second_level(result: BoltStatementResult, keys: set):
    array = []
    for a in [dict(r['a'].items()) for r in result.records()]:
        aa = {}
        for k in a:
            if k in keys:
                aa[k] = json.loads(a[k])
            else:
                aa[k] = a[k]
        array.append(aa)
    return array


def flight_records_from_string(result: BoltStatementResult, keys: set):
    res = []
    for item in result.records():
        flight_record = item["flight_record"]
        fr = {"date": flight_record["date"], "arrival": json.loads(flight_record["arrival"]),
              "departure": json.loads(flight_record["departure"]), "details": json.loads(flight_record["details"]),
              "flags": json.loads(flight_record["flags"]), "time": json.loads(flight_record["time"])}
        res.append(fr)
    return res


def flight_records_from_apoc(result: BoltStatementResult, keys: set):
    return [r['flight_record'] for r in result.records()]


def flight_records_from_maps(result: BoltStatementResult, keys: set):
    return [r['flight_record'] for r in result.records()]
