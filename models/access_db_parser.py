import os
from typing import Union, List
from pathlib import Path
import logging
import jaydebeapi
import xmltodict
jars_base_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "ucan_jars")
UCANACCESS_JARS_PATHS = [os.path.join(jars_base_file, file_name) for file_name in os.listdir(jars_base_file)]
CLASS_PATH = ":".join(UCANACCESS_JARS_PATHS)

logger = logging.getLogger(__name__)

def scale_dim(record):
    return float(record)


def convert_outlines(outlines_dict, rel_x, rel_y):
    outlines = []
    current_x, current_y = rel_x, rel_y
    for discribtor in outlines_dict:
        _type = discribtor['@type']
        begin = discribtor.get("begin", None)
        end = discribtor.get('end', None)
        if begin and end:
            pt1 = [current_x, current_y]
            pt2 = [current_x, current_y]
            if "x" in begin:
                pt1[0] = scale_dim(begin["x"])
            if "y" in begin:
                pt1[1] = scale_dim(begin["y"])

            if "x" in end:
                pt2[0] = scale_dim(end["x"])
            if "y" in end:
                pt2[1] = scale_dim(end["y"])
            outlines.append((pt1, pt2))
    return outlines

class RoutePath(object):
    def __init__(self, route_width, route_length, route_depth, route_posX, route_posY, route_posZ, route_outline, tool_id):
        self.width = route_width
        self.length = route_length
        self.depth = route_depth
        self.posX = route_posX
        self.posY = route_posY
        self.posZ = route_posZ
        self.outline = route_outline
        self.tool_id  = tool_id
    
    def __repr__(self) -> str:
        return(f"""
        *************************** route path *********************
        width:{self.width}
        length:{self.length}
        posx:{self.posX}
        posy:{self.posY}
        outline:{self.outline}
        tool_id:{self.tool_id}

        """)

    def get_outer_dims(self):
        return scale_dim(self.length), scale_dim(self.width)

    def get_outlines(self):
        json_content = xmltodict.parse(self.outline)
        outlines = []
        for key in json_content:
             json_content = json_content[key]["geometry"]["entity"]
             outlines.extend( convert_outlines(json_content, scale_dim(self.posX), scale_dim(self.posY)))
        return outlines

    def get_init_pos(self):
        return scale_dim(self.posX), scale_dim(self.posY)

class Part(object):
    def __init__(self, part_id,  width, length, shaped, outline, operations: list):
        self.part_id = part_id
        self.width = width
        self.length = length
        self.shaped = shaped
        self.outline = outline
        self.operations = operations

    def __repr__(self) -> str:
        return f"""
        ********  part ******
        width:{self.width}
        length:{self.length}
        shaped:{self.shaped}
        outline:{self.outline}
        operations:{self.operations}
        """
    def get_outer_dims(self):
        return scale_dim(self.length), scale_dim(self.width)

    def get_outlines(self):
        json_content = xmltodict.parse(self.outline)["template"]["geometry"]["entity"]
        return convert_outlines(json_content, 0, 0)

class MDBFileConnector:
    db_connection: Union[jaydebeapi.Connection, None] = None
    db_cursor: Union[jaydebeapi.Cursor, None] = None
    is_connected: bool = False

    def __init__(self, file_path: Path):
        self.__db_file_path = file_path

    def connect(self) -> bool:
        connected = False
        logger.debug(f"tying connect to access db file {self.__db_file_path}")
        try:
            self.db_connection = jaydebeapi.connect("net.ucanaccess.jdbc.UcanaccessDriver",
                                                    f"jdbc:ucanaccess://{str(self.__db_file_path)}", ["", ""],
                                                    CLASS_PATH)
        except Exception as e:
            print(e)
            logger.exception(f"Failed to connect to {self.__db_file_path} > {e}")
        else:
            logger.info(f"connected to {self.__db_file_path}")
            connected = True
            self.db_cursor = self.db_connection.cursor()
            self.is_connected = True
        return connected

    def execute(self, qur: str, auto_commit: bool = False):
        if not self.is_connected:
            raise RuntimeError("not connected...")
        self.db_cursor.execute(qur)
        if auto_commit:
            self.db_connection.commit()

    def close(self):
        if self.is_connected:
            self.db_connection.close()

    def list_tables(self) -> List[str]:
        if not self.is_connected:
            self.connect()
        md = self.db_connection.jconn.getMetaData()
        tables_result_set = md.getTables(None, None, "%", None)
        table_names = []
        while tables_result_set.next():
            table_names.append(tables_result_set.getString(3))
        return table_names

    def get_table_columns(self, table_name: str) -> List[str]:
        if not self.is_connected:
            self.connect()
        md = self.db_connection.jconn.getMetaData()
        columns_result_set = md.getColumns(None, None, table_name, None)
        columns = []
        while columns_result_set.next():
            columns.append(columns_result_set.getString(4))
        return columns

    def get_table_content(self, table_name: str) -> List[dict]:
        if not self.is_connected:
            self.connect()
        self.execute(f"SELECT * FROM {table_name}")
        columns = self.get_table_columns(table_name)
        content = []
        for row in self.db_cursor.fetchall():
            content.append(dict(zip(columns, row)))
        return content


    def get_parts(self, part_id) -> list:
        parts = []
        qur = f"""SELECT ID,  Width, Length,Shaped, Outline FROM Parts s where [ID]={part_id};"""
        self.db_cursor.execute(qur)
        for _id,  width, length, shaped, outline in self.db_cursor.fetchall():
            route_qur = f"""SELECT Width, Length, Depth, PosX, PosY, PosZ, Outline, ToolID FROM PartOperations s where PartID={_id} and Name="Route Path";"""
            self.db_cursor.execute(route_qur)
            paths = []
            for route_width, route_length, route_depth, route_posX, route_posY, route_posZ, route_outline, tool_id in self.db_cursor.fetchall():
                path = RoutePath(float(route_width), float(route_length), float(route_depth), float(route_posX), float(route_posY), float(route_posZ), route_outline, tool_id)
                paths.append(path)
            part = Part(_id,  float(width), float(length), bool(shaped), outline, paths)
            print("*********************** part detected *************************************")
            print(part)
            parts.append(part)
        return parts

if __name__ == "__main__":
    PATH = "/home/mohamed/workspace/upwork/tld_files/Job-Manual.tld"
    db = MDBFileConnector(PATH)
    db.connect()
    db.get_parts()