from models import OrbitPath, NearEarthObject
import csv


class NEODatabase(object):
    """
    Object to hold Near Earth Objects and their orbits.
    To support optimized date searching, a dict mapping of all orbit date paths to the Near Earth Objects
    recorded on a given day is maintained. Additionally, all unique instances of a Near Earth Object
    are contained in a dict mapping the Near Earth Object name to the NearEarthObject instance.
    """

    def __init__(self, filename):
        """
        :param filename: str representing the pathway of the filename containing the Near Earth Object data
        """
        # TODO: What data structures will be needed to store the NearEarthObjects and OrbitPaths?
        # TODO: Add relevant instance variables for this.
        
        self.filename = filename
        self.NearEarthObjects = dict()
        self.OrbitPaths = []

    def load_data(self, filename=None):
        """
        Loads data from a .csv file, instantiating Near Earth Objects and their OrbitPaths by:
           - Storing a dict of orbit date to list of NearEarthObject instances
           - Storing a dict of the Near Earth Object name to the single instance of NearEarthObject
        :param filename:
        :return:
        """

        if not (filename or self.filename):
            raise Exception('Cannot load data, no filename provided')

        filename = filename or self.filename

        # TODO: Load data from csv file.
        with open(filename, 'r') as f:
            csvfile = csv.DictReader(f, delimiter=",")
            
        # TODO: Where will the data be stored?
            for row in csvfile:
                orb_date = row['close_approach_date']
                neo_name = row['name']

                neoModel = {
                    "id": row["neo_reference_id"],
                    "name": row["name"], 
                    "diameter_min_km": float(row["estimated_diameter_min_kilometers"]),
                    "is_hazardous": True if row["is_potentially_hazardous_asteroid"] == "True" else False,
                    "orbits": []
                    #"orbit_dates": []
                    }

                orbitPathModel = {
                    "name" : row["name"],
                    "distance": float(row["miss_distance_kilometers"]),
                    "orbit_date": row["close_approach_date_full"]
                }

                orbitPath = OrbitPath(**orbitPathModel)

                self.OrbitPaths.append(orbitPath)

                neoObject = NearEarthObject(**neoModel)

                if orb_date in self.NearEarthObjects:
                    neoObject.update_orbits(orbitPath)
                    self.NearEarthObjects[orb_date] += [neoObject]
                else:
                    neoObject.update_orbits(orbitPath)
                    self.NearEarthObjects[orb_date] = [neoObject]

        return None