from PySide2 import QtCore
from pathlib import Path
from models.access_db_parser import RoutePath, Part, MDBFileConnector
from typing import List, Dict, Any


class TldFileScanner(QtCore.QThread):
    is_running = False
    ploting_metadata_available_signal = QtCore.Signal(list)
    def __init__(self, order_folder_path: Path, tld_part_id: int):
        """
        tld file is access db file i should connect to it and get the data
        :param order_folder_path: path that contains all the materials for the order
        and each material has a tld file
        """
        super().__init__()
        self.order_folder_path = order_folder_path
        self.tld_part_id = tld_part_id


    def run(self):
        TldFileScanner.is_running = True
        tld_file_content = []
        for folder in self.order_folder_path.iterdir():
            if folder.is_dir():
                for file in folder.iterdir():
                    if file.suffix == ".tld":
                        print(f"check {file}")
                        tld_file_content = self.get_tld_part_content(file, self.tld_part_id)
                        if len(tld_file_content) > 0:
                            print("content detected ")
                            break
            if len(tld_file_content) > 0:
                break
        if len(tld_file_content) > 0:
            self.ploting_metadata_available_signal.emit(tld_file_content)
        else:
            print("no content ")
        TldFileScanner.is_running = False

    def get_plotting_metadata(self, tld_file_content: List[Part]) -> List[Dict[str, Any]]:
        """
        get the plotting metadata from the tld file content
        :param tld_file_content: the content of the tld file
        :return: the plotting metadata
        """
        meta_data = []
        for part in tld_file_content:
            part_dict = {}
            part_dict["dims"] = part.get_outer_dims()
            part_dict["outlines"] = []
            if part.shaped:
                part_dict["outlines"]= part.get_outlines()
            part_dict["operations"] = []
            for operation in part.operations:
                operation_dict = {}
                length, width = operation.get_outer_dims()
                operation_dict["dims"] = operation.get_outer_dims()
                xpos, ypos = operation.get_init_pos()
                part_dict["rectangle"] = ((xpos, ypos), (xpos+width, ypos+length))
                operation_dict["outlines"] = operation.get_outlines()
                part_dict["operations"].append(operation_dict)
            meta_data.append(part_dict)
        return meta_data

    @staticmethod
    def get_tld_part_content(tld_file_path:Path, tld_part_id:int) -> List[Part]:
        """
        get the content of the tld file
        :param tld_file_path: path to the tld file
        :return:
        """
        if tld_file_path:
            # now I have to parse the tld file and get the data
            db = MDBFileConnector(tld_file_path)
            db.connect()
            parts = db.get_parts(tld_part_id)
            db.close()
            return parts
        return []