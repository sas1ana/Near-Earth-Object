from collections import namedtuple,defaultdict
from enum import Enum

from exceptions import UnsupportedFeature
from models import NearEarthObject, OrbitPath

import datetime
import operator

class DateSearch(Enum):
    """
    Enum representing supported date search on Near Earth Objects.
    """
    between = 'between'
    equals = 'equals'

    @staticmethod
    def list():
        """
        :return: list of string representations of DateSearchType enums
        """
        return list(map(lambda output: output.value, DateSearch))


class Query(object):
    """
    Object representing the desired search query operation to build. The Query uses the Selectors
    to structure the query information into a format the NEOSearcher can use for date search.
    """

    Selectors = namedtuple('Selectors', ['date_search', 'number', 'filters', 'return_object'])
    DateSearch = namedtuple('DateSearch', ['type', 'values'])
    ReturnObjects = {'NEO': NearEarthObject, 'Path': OrbitPath}

    def __init__(self, **kwargs):
        """
        :param kwargs: dict of search query parameters to determine which SearchOperation query to use
        """
        # TODO: What instance variables will be useful for storing on the Query object?
        self.number = kwargs['number']
        self.date = kwargs['date'] if 'date' in kwargs else None
        self.start_date = kwargs['start_date'] if 'start_date' in kwargs else None
        self.end_date = kwargs['end_date']  if 'end_date' in kwargs else None
        self.filters = kwargs['filter'] if 'filter' in kwargs else None
        self.return_object = kwargs['return_object']

    def build_query(self):
        """
        Transforms the provided query options, set upon initialization, into a set of Selectors that the NEOSearcher
        can use to perform the appropriate search functionality
        :return: QueryBuild.Selectors namedtuple that translates the dict of query options into a SearchOperation
        """

        # TODO: Translate the query parameters into a QueryBuild.Selectors object
        
        if (self.date):
            date_search = Query.DateSearch(DateSearch.equals,self.date)
        else:
            date_search = Query.DateSearch(DateSearch.between,[self.start_date, self.end_date])
        
        query = Query.Selectors(date_search, self.number, self.filters, Query.ReturnObjects[self.return_object])
        
        return query

class Filter(object):
    """
    Object representing optional filter options to be used in the date search for Near Earth Objects.
    Each filter is one of Filter.Operators provided with a field to filter on a value.
    """
    # TODO: Create a dict of filter name to the NearEarthObject or OrbitalPath property
    Options = {
        "diameter"      : "diameter_min_km",
        "is_hazardous"  : "is_hazardous",
        "distance"      : "miss_distance_kilometers"
    }
    
    # TODO: Create a dict of operator symbol to an Operators method, see README Task 3 for hint
    Operators = {
        ">" : operator.gt,
        "=" : operator.eq,
        ">=": operator.ge
    }

    def __init__(self, field, object, operation, value):
        """
        :param field:  str representing field to filter on
        :param field:  str representing object to filter on
        :param operation: str representing filter operation to perform
        :param value: str representing value to filter for
        """
        self.field = field
        self.object = object
        self.operation = operation
        self.value = value

    @staticmethod
    def create_filter_options(filter_options):
        """
        Class function that transforms filter options raw input into filters
        :param input: list in format ["filter_option:operation:value_of_option", ...]
        :return: defaultdict with key of NearEarthObject or OrbitPath and value of empty list or list of Filters
        """

        # TODO: return a defaultdict of filters with key of NearEarthObject or OrbitPath and value of empty list or list of Filters
        defaultdict = {"NEO": [], "ORB": []}

        if filter_options == None or filter_options == []:
            return defaultdict

        else:
            for filter_type in filter_options:
                x = filter_type.split(":")

                if x[0] in ["diameter", Filter.Options["is_hazardous"]]:
                    defaultdict["NEO"].append(Filter(x[0], NearEarthObject, x[1], x[2]))
                
                if x[0] == Filter.Options["distance"]:
                    defaultdict["ORB"].append(Filter(x[0], OrbitPath, x[1], x[2]))
                
        return defaultdict
                

    def apply(self, results):
        """
        Function that applies the filter operation onto a set of results
        :param results: List of Near Earth Object results
        :return: filtered list of Near Earth Object results
        """
        # TODO: Takes a list of NearEarthObjects and applies the value of its filter operation to the results
        
        filtered_list = list()
        if self.field == "diameter":
            filtered_list = list(filter(
                lambda neo: Filter.Operators[self.operation](getattr(neo,Filter.Options[self.field]), float(self.value)), results)
            )
            return filtered_list
            
        if self.field == "is_hazardous":
            is_hazardous = True if self.value == 'True' else False
            for neo in results:
                if Filter.Operators[self.operation](neo.is_potentially_hazardous_asteroid, is_hazardous):
                    filtered_list += [neo]
            return filtered_list

        if self.field == "distance":
            all_orbits = []
            for neo in results:
                for orb in neo.orbits:
                    all_orbits += [orb]
            unique_orbits = set()
            filtered_orbits = []
            for orbit in all_orbits:
                date_name = f'{orbit.close_approach_date}.{orbit.neo_name}'
                if date_name not in unique_orbits:
                    
                    if Filter.Operators[self.operation](orbit.miss_distance_kilometers, float(self.value)):
                        filtered_orbits.append(orbit)
                        filtered_list += [neo]
            return filtered_list


class NEOSearcher(object):
    """
    Object with date search functionality on Near Earth Objects exposed by a generic
    search interface get_objects, which, based on the query specifications, determines
    how to perform the search.
    """

    def __init__(self, db):
        """
        :param db: NEODatabase holding the NearEarthObject instances and their OrbitPath instances
        """
        self.db = db
        # TODO: What kind of an instance variable can we use to connect DateSearch to how we do search?
        self.searchObject = []

    # Search Object on a single date
    def equals_search(self, date_search):
        """
        Instance method to perform DateSearch on the db to extract NearEarthObject 
        from a single date.
        Once the extraction is complete, return a list of the NearEarthObject obtained
        :param date_search: str representing the date to search on
        :return: list of NearEarthObjects
        """
        neo = {}
        for n in self.db.NearEarthObjects[date_search]:
            neo_name = n.name
            if not neo_name in neo:
                neo[neo_name] = n
        return list(neo.values())

    # Search Object between start and end dates
    def between_search(self, date_search):
        """
        Instance method to perform DateSearch on the db to extract NearEarthObject 
        from a a range of dates.
        Once the extraction is complete, return a list of the NearEarthObject obtained
        :param date_search: list containing a pair of dates to search from
        :return: list of NearEarthObjects
        """

        neo = {}
        a, b, c = tuple(date_search[0].split("-"))
        d, e ,f = tuple(date_search[1].split("-"))
                        
        start_date = datetime.date(int(a),int(b),int(c))
        end_date = datetime.date(int(d),int(e),int(f)+1)
        daterange = [start_date + datetime.timedelta(days=x) for x in range(0, (end_date-start_date).days)]

        for d in daterange:
            d = d.strftime("%Y-%m-%d")
            for n in self.db.NearEarthObjects[d]:
                neo_name = n.name
                if not neo_name in neo:
                    neo[neo_name] = n
        return list(neo.values())

    def get_objects(self, query):
        """
        Generic search interface that, depending on the details in the QueryBuilder (query) calls the
        appropriate instance search function, then applys any filters, with distance as the last filter.
        Once any filters provided are applied, return the number of requested objects in the query.return_object
        specified.
        :param query: Query.Selectors object with query information
        :return: Dataset of NearEarthObjects or OrbitalPaths
        """
        # TODO: This is a generic method that will need to understand, using DateSearch, how to implement search
        # TODO: Write instance methods that get_objects can use to implement the two types of DateSearch your project
        # TODO: needs to support that then your filters can be applied to. Remember to return the number specified in
        # TODO: the Query.Selectors as well as in the return_type from Query.Selectors
        filters = Filter.create_filter_options(query.filters) if query.filters is not None else None

        if query.date_search.type == DateSearch.equals:
            results = self.equals_search(query.date_search.values)
            
            if filters is not None:
                for filt in filters["NEO"]:
                    results = filt.apply(results)
                for filt in filters["ORB"]:
                    results = filt.apply(results)
                
            return results[:query.number]

        if query.date_search.type == DateSearch.between:
            results = self.between_search(query.date_search.values)
            
            if filters is not None:
                for filt in filters["NEO"]:
                    results = filt.apply(results)
                for filt in filters["ORB"]:
                    results = filt.apply(results)

            return results[:query.number]