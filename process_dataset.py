from utils import conversion_utils
from utils import metadata_utils
import fire
import os

def main(ds_dir: str = "MUSCUTS", metadata_json_dir: str = "keys", log_dir: str = "log"):
    logs_dir = os.path.join(ds_dir, log_dir)
    
    os.makedirs(logs_dir, exist_ok=True)
    conversion_utils.convert_dataset(ds_dir=ds_dir, log_dir=logs_dir)
    metadata_utils.retrieve_metadata(metadata_json_dir=metadata_json_dir, root_dir=ds_dir, log_dir=logs_dir)
    metadata_utils.copy_precomputed_partitions(ds_dir=ds_dir, partition_folder="partitions")

if __name__ == "__main__":
    fire.Fire(main)