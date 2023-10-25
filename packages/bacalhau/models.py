from pydantic import BaseModel



class DataPreprocessing(BaseModel):
    storage_files_path: str

