import sqlite3

## example from the bgt, as explained in the following tutorial: https://tudelft3d.github.io/3dfier/generate_lod1.html

class DBCreator:
    """
    this package converts the generated LAZ point cloud and polygon elevation model
    format files and details into the DB format.
    """
    
    sqlite: sqlite3
      
    def __init__(self, db_file_name):
        self.sqlite = sqlite3.connect(db_file_name + '.sqlite3')
        self.cursor = self.sqlite.cursor()
    
    def read_all_data(self, table_name):
        query = f"SELECT * FROM {table_name}"
        self.cursor.execute(query)
        data = self.cursor.fetchall()
        return data

    def read_data_by_id(self, table_name, id):
        query = f"SELECT * FROM {table_name} WHERE id = ?"
        self.cursor.execute(query, (id,))
        data = self.cursor.fetchone()
        return data