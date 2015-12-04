from mock import Mock as MagicMock
from BioFlow.utils.log_behavior import logger

logger.debug('Mocking DB_IO module')


def look_up_annotation_set(supplied_list):
    return supplied_list, [(elt, '') for elt in supplied_list], ['' for _ in supplied_list]
