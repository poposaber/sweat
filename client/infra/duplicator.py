import os
import shutil
import logging
from .errors import SourceNotFoundError, DuplicatorError

logger = logging.getLogger(__name__)

class Duplicator:
    def __init__(self, source_path: str = "client/template"):
        self.source_path = source_path

    def duplicate(self, destination_path: str):
        """
        Duplicates the file/directory in source_path to destination_path.
        
        Args:
            destination_path: The full path where the template should be copied.
            
        Returns:
            True if successful, False otherwise.
        """
        if not os.path.exists(self.source_path):
            logger.error(f"Source path does not exist: {self.source_path}")
            raise SourceNotFoundError(f"Source path does not exist: {self.source_path}")

        try:
            # dirs_exist_ok=True allows copying into an existing directory (merging/overwriting)
            shutil.copytree(self.source_path, destination_path, dirs_exist_ok=True)
            logger.info(f"Duplicated {self.source_path} to {destination_path}")
        except Exception as e:
            logger.exception(f"Failed to duplicate template: {e}")
            raise DuplicatorError(f"Failed to duplicate template: {e}") from e
