"""
Wrapper module around the retriever of laplacian matrices from neo4j graphs
"""
import pickle
import json
import hashlib
import numpy as np
from time import time
from itertools import izip

from BioFlow.utils.io_Routines import write_to_csv, dump_object, undump_object
from BioFlow.utils.log_behavior import get_logger

log = get_logger(__name__)


class LaplacianRetriever(object):
    """
    Base class for the functions pulling a laplacian matrix out of the neo4j database
    """

    # TODO: control dumping/undumping behavior with a [(fileName, [self.property])] controller

    def __init__(self):
        self.init_time = time()
        self.partial_time = time()

        self.analytic_uniprots = []
        self.current_accumulator = np.zeros((2, 2))
        self.node_current = {}
        self.uniprots_2_voltage_and_circulation = {}

        self.memoization_dump_location = ''  # Dumps.Interactome_Analysis_memoized
        self.main_set = {}                   # sorted set that decides md_5 behavior
        self.md5_hash_variables = []         # properties of self that need to be in md5 hash

        self.full_dump_map = []

    def pretty_time(self):
        """ Pretty formatted timing since last call message """
        it, pt = (round(time() - self.init_time),
                  round(time() - self.partial_time))
        timing_message = 'total: %s m %s s, \t partial: %s m %s s' % (
            int(it) / 60, it % 60, int(pt) / 60, pt % 60)
        self.partial_time = time()
        return timing_message

    def _time(self):
        """ Gives and internal timing message """
        time_difference = time() - self.partial_time
        return time_difference

    @staticmethod
    def meta_dump(instructions_list):
        """
        A meta-method to dump sets of objects

        :param instructions_list: dump behavior controlling list: [(where to dump, [what to dump])]
        """
        for dump_file, object_to_dump in instructions_list:
            dump_object(dump_filename=dump_file, object_to_dump=object_to_dump)

    @staticmethod
    def meta_undump(instructions_list):
        """
        A meta-method to undump a set of objects depending in a controlling dict

        Will undump dumped objects towards pointers that were requested to be dumped. In case
        lengths of list of objects to be undumped from a file differ from expected, will

        :param instructions_list: dump behavior controlling list: [(where to dump, [what to dump])]
        """
        # TODO: check that this will work. Another option is to use a self.__getitem__
        for dump_file, objects_to_set in instructions_list:
            undump_list = undump_object(dump_filename=dump_file)

            if len(undump_list) != len(objects_to_set):
                log.error('Undumping: different instruction list lengths. %s stored, %s requested',
                          len(undump_list), len(objects_to_set))
                raise Exception('Undumping with different instruction list lengths')

            else:
                for object_to_set, dumped_object in izip(objects_to_set, undump_list):
                    object_to_set = dumped_object

    def md_5_hash(self):
        """
         Computes md5 hash for the object
        :return:
        """
        sorted_initset = sorted(self.main_set.keys(), key=str.lower)
        data = [sorted_initset] + self.md5_hash_variables
        md5 = hashlib.md5(json.dumps(data, sort_keys=True)).hexdigest()
        return str(md5)

    def dump_memoized(self):
        """
        Dumps a memoization-compatible file
        :return:
        """
        md5 = hashlib.md5(
            json.dumps(
                sorted(
                    self.analytic_uniprots),
                sort_keys=True)).hexdigest()
        payload = {
            'UP_hash': md5, 'sys_hash': self.md5_hash(), 'size': len(
                self.analytic_uniprots), 'UPs': pickle.dumps(
                self.analytic_uniprots), 'currents': pickle.dumps(
                (self.current_accumulator, self.node_current)), 'voltages': pickle.dumps(
                    self.uniprots_2_voltage_and_circulation)}
        dump_object(self.memoization_dump_location, payload)

    def undump_memoized(self):
        """
        :return: undumped memoized analysis
        :rtype: dict
        """
        return undump_object(self.memoization_dump_location)

    def rebuild(self):
        """ Rebuilds the laplacian and names_mappings """
        pass

    def store(self):
        """ Stores the laplacian and names mappings in the dump stores"""
        pass

    def load(self):
        """ Loads the laplacian and names mappings from the dump stores """
        pass

    def build_laplacian(self):
        """
        Constructs laplacian with the proper matrices
        """
        pass

    def calculate_current_for_sample(self):
        """ calculates the current circulation for the sample
        """
        pass

    def sample_current(self):
        """
        performs the current sampling for comparison.

        Conserves random node-pairs resistances and average inter-node tension in case of
        """
        pass

    def compare_circulation_to_reference(self):
        """
        compares actual sample to a random sample from the background

        Compares the obtained current to the 95% estimation of chance that flow would be observed
        on a random sample of equal size analyzed with the same approach
        """
        pass

    def output_as_gdf(self):
        """returns the laplacian graph and it's circulation state"""
        pass


# Overall ideas:
#   - split into three objects.
#       1). Performing a pull of the system following a list of instructions (that can be
#        re-implemented in the subclasses
#       2) Performing a current retrieval operation
#       3) Rebuilding/storage/IO with Mongo
#       4) Add in import/export statement that would operate on the build laplacian and node
#        property mapping system
#       Remove localization of the uniprot nodes and databases.=> we are not really using it,
        # and if we were, the mechanism to use it would be of the instantiations, entirely
        # different from the current one and allowing for same operations on organs or other
        # elements.