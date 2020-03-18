class NearEarthObject(object):
    """
    Object containing data describing a Near Earth Object and it's orbits.
    # TODO: You may be adding instance methods to NearEarthObject to help you implement search and output data.
    """

    def __init__(self, **kwargs):
        """
        :param kwargs:    dict of attributes about a given Near Earth Object, only a subset of attributes used
        """
        # TODO: What instance variables will be useful for storing on the Near Earth Object?
        self.id = kwargs["id"]
        self.name = kwargs["name"]
        self.diameter_min_km = kwargs["diameter_min_km"]
        self.is_potentially_hazardous_asteroid = kwargs["is_hazardous"]
        self.orbits = kwargs["orbits"]

    def update_orbits(self, orbit):
        """
        Adds an orbit path information to a Near Earth Object list of orbits
        :param orbit: OrbitPath
        :return: None
        """

        # TODO: How do we connect orbits back to the Near Earth Object?
        self.orbits.append(orbit)

class OrbitPath(object):
    """
    Object containing data describing a Near Earth Object orbit.
    # TODO: You may be adding instance methods to OrbitPath to help you implement search and output data.
    """

    def __init__(self, **kwargs):
        """
        :param kwargs:    dict of attributes about a given orbit, only a subset of attributes used
        """
        # TODO: What instance variables will be useful for storing on the Near Earth Object?
        self.neo_name = kwargs["name"]
        self.miss_distance_kilometers = kwargs["distance"]
        self.close_approach_date = kwargs["orbit_date"]