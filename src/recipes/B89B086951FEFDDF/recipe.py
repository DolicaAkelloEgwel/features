import numpy as np


class Point:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
        self.id = 0

    def set_id(self, index):
        self.id = index

    def point_string(self):
        return " ".join([str(self.x), str(self.y), str(self.z)]) + "\n"


class OFFFileCreator:
    def __init__(self, z, units):

        self.file = "OFF\n"
        self.vertices = []
        self.vertex_counter = 0
        self.faces = []
        self.front_vertices = []
        self.back_vertices = []
        self.z = z
        self.degrees = units == b"deg"

    def find_x(self, radius, theta):
        if self.degrees:
            return radius * np.cos(np.deg2rad(theta))

        return radius * np.cos(theta)

    def find_y(self, radius, theta):
        if self.degrees:
            return radius * np.sin(np.deg2rad(theta))

        return radius * np.sin(theta)

    def create_mirrored_points(self, r, theta):

        x = self.find_x(r, theta)
        y = self.find_y(r, theta)

        return Point(x, y, self.z), Point(x, y, -self.z)

    def create_and_add_point_set(self, radius, slit_height, slit_edge):

        outer_front_point, outer_back_point = self.create_mirrored_points(
            radius, slit_edge
        )
        inner_front_point, inner_back_point = self.create_mirrored_points(
            slit_height, slit_edge
        )

        self.add_vertex(outer_front_point)
        self.add_vertex(outer_back_point)
        self.add_vertex(inner_front_point)
        self.add_vertex(inner_back_point)

        return [
            outer_front_point,
            outer_back_point,
            inner_front_point,
            inner_back_point,
        ]

    def add_vertex(self, point):

        point.set_id(self.vertex_counter)
        self.vertices.append(point)
        self.vertex_counter += 1

    def add_vertices(self, points):

        for point in points:
            self.add_vertex(point)

    def add_face(self, points):

        ids = [point.id for point in points]
        self.faces.append(ids)

    def add_number_string_to_file(self, numbers):

        self.file += " ".join([str(num) for num in numbers]) + "\n"

    def add_vertex_to_file(self, vertex):

        self.file += vertex.point_string()

    def add_face_to_file(self, face):

        n_vertices = len(face)
        self.add_number_string_to_file([n_vertices] + face)

    def create_file(self):

        n_vertices = len(self.vertices)
        n_faces = len(self.faces)

        self.add_number_string_to_file([n_vertices, n_faces, 0])

        for vertex in self.vertices:
            self.add_vertex_to_file(vertex)

        for face in self.faces:
            self.add_face_to_file(face)

        return self.file


class recipe:
    """
    Generate OFF files from the NXdisk_choppers that are present in the NeXus file.

    Proposed by: dolica.akello-egwel@stfc.ac.uk
    """

    def __init__(self, filedesc, entrypath):
        """
        Recipes are required to set a descriptive self.title

        :param filedesc: h5py file object of the NeXus/HDF5 file
        :param entrypath: path of the entry containing this feature
        """

        self.file = filedesc
        self.entry = entrypath
        self.title = "Create an OFF file from an NXdisk_chopper"

        self.choppers = None
        self.resolution = 20

    def find_disk_choppers(self):
        """
        Find all of the disk_choppers contained in the file and return them in a list.
        """
        self.choppers = [self.file["entry"]["instrument"]["example_chopper"]]

    @staticmethod
    def get_chopper_data(chopper):
        """
        Extract radius, slit_height, and slit_edges data from a given chopper group.
        """
        radius = chopper["radius"][()]
        slit_height = chopper["slit_height"][()]
        slit_edges = chopper["slit_edges"][()]
        units = chopper["slit_edges"].attrs["units"]

        return radius, slit_height, slit_edges, units

    def generate_off_file(self, chopper):
        """
        Create an OFF file from a given chopper.
        """
        z = 50
        radius, slit_height, slit_edges, units = self.get_chopper_data(chopper)

        off_creator = OFFFileCreator(z, units)

        point_set = off_creator.create_and_add_point_set(
            radius, slit_height, slit_edges[0]
        )

        prev_outer_front = first_outer_front = point_set[0]
        prev_outer_back = first_outer_back = point_set[1]
        prev_inner_front = first_inner_front = point_set[2]
        prev_inner_back = first_inner_back = point_set[3]

        for i in range(1, len(slit_edges)):

            current_outer_front, current_outer_back, current_inner_front, current_inner_back = off_creator.create_and_add_point_set(
                radius, slit_height, slit_edges[i]
            )

            if i % 2:
                pass

            else:
                pass

            prev_outer_front = current_outer_front
            prev_outer_back = current_outer_back
            prev_inner_front = current_inner_front
            prev_inner_back = current_inner_back

        file = off_creator.create_file()
        print(file)

    def process(self):
        """
        Recipes need to implement this method and return information which
        is useful to a user and instructive to a person reading the code.
        See some of the recommended examples for inspiration what to return.

        :return: the essence of the information recorded in this feature
        """

        self.find_disk_choppers()

        if not self.choppers:
            return "Unable to find disk choppers."

        else:

            for chopper in self.choppers:
                self.generate_off_file(chopper)
