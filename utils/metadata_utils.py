import glob
# import torchaudio
import shutil
import os
import json
import re
from pathlib import Path
import os, json, glob, re

def normalize_path(path):
    path = path.replace("\\", "/").replace("//", "/")
    # make sure to encode correctly any special characters
    return path.encode("utf-8").decode("utf-8")


def remove_extensions(file_path, known_extensions={".musicxml.xml", ".krn", ".ly", ".mp3", ".png"}):
    path = Path(file_path)
    name = path.name  # Get just the filename
    for ext in known_extensions:
        if name.endswith(ext):  
            name = name[: -len(ext)]  # Remove only the matched extension
    return name  # Return cleaned filename


def check_modalities_file(ds_dir, file_path, extensions={".mp3", ".png", ".krn", ".ly", ".musicxml.xml"}, log_dir="logs"):
    # make sure that the mp3 can be opened with torchaudio
    try:
        audio_path = os.path.join(ds_dir, file_path + ".mp3")
        # torchaudio.load(audio_path)
    except Exception as e:
        with open(os.path.join(log_dir, "metadata_retrieval.log"), "a", encoding="utf-8") as log_f:
            log_f.write(f"Audio file {file_path + '.mp3'} could not be opened with torchaudio: {str(e)[:100]}\n")
        return False
    
    for ext in extensions:
        if not os.path.exists(os.path.join(ds_dir, file_path + ext)):
            with open(os.path.join(log_dir, "metadata_retrieval.log"), "a", encoding="utf-8") as log_f:
                log_f.write(f"File {file_path + ext} not found in {ds_dir}\n")
            return False
    return True


def extract_cut_number(filename):
    """Extracts the cut number from a filename using regex."""
    match = re.search(r'_cut_(\d+)', filename)
    return int(match.group(1)) if match else float('inf')  # Default to infinity if no match


def load_json_list(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def retrieve_metadata(metadata_json_dir: str, ds_dir: str, log_dir: str):

    # ---- Load JSON collections ----
    print("Retrieving metadata from MUSCAT to MUSCUTS dataset...")
    scores = load_json_list(os.path.join(metadata_json_dir, "MUSCAT.scores.json"))
    composers = load_json_list(os.path.join(metadata_json_dir, "MUSCAT.composers.json"))
    audios = load_json_list(os.path.join(metadata_json_dir, "MUSCAT.audios.json"))
    instruments = load_json_list(os.path.join(metadata_json_dir, "MUSCAT.instruments.json"))

    # Convert scores + audios into map structures for find_one replacement
    scores_by_path = {s["pathToFolder"]: s for s in scores}
    audios_by_path = {a["pathToFile"]: a for a in audios}
    composers_by_id = {c["_id"]["$oid"]: c for c in composers}
    instruments_by_id = {i["_id"]["$oid"]: i for i in instruments}
    log_file = os.path.join(log_dir, "metadata_retrieval.log")
    
    all_files = []
    # Main traversal
    reserved_folders = ["log", "partitions", "embeddings", "embddings_balanced"]
    for composer_folder in os.listdir(ds_dir):
        if (not os.path.isdir(os.path.join(ds_dir, composer_folder))) or (composer_folder in reserved_folders):
            continue

        for score_folder in os.listdir(os.path.join(ds_dir, composer_folder)):
            score_path = os.path.join(composer_folder, score_folder)
            # if score path contains any "\\", or "//", replace with "/"
            score_doc = scores_by_path.get(f"/{normalize_path(score_path)}")
            if score_doc is None:
                with open(log_file, "a", encoding="utf-8") as log_f:
                    log_f.write(f"Score {score_path} not found in JSON database \n")
                continue

            score_title = score_doc["title"]

            composer_doc = composers_by_id.get(score_doc["composer"]["$oid"], None)
            if composer_doc is not None:
                composer_name = composer_doc["name"]
            else:
                with open(log_file, "a", encoding="utf-8") as log_f:
                    log_f.write(f"Composer {score_doc['composer']} not found for score {score_path}\n")
                composer_name = "Unknown"

            mp3_files = glob.glob(f"{os.path.join(ds_dir, score_path)}/*.mp3")
            audio_files = list(set([re.split("_-_cut_", os.path.basename(f))[0] for f in mp3_files]))

            for audio_file in audio_files:
                cut_files = glob.glob(f"{os.path.join(ds_dir, score_path)}/*{audio_file}_-_cut_*")
                cuts = list(set([remove_extensions(c) for c in cut_files]))
                cuts.sort(key=extract_cut_number)
                all_files.extend(os.path.join(score_path, cut) for cut in cuts)

                metadata_file = f"{os.path.join(ds_dir, score_path, audio_file)}.json"
                if os.path.exists(metadata_file):
                    print(f"Metadata file {metadata_file} exists. Skipping.") 
                    continue

                # ---- Replace Mongo find_one({"pathToFile": f"/{audio_path}"}) ----
                audio_path = f"/{normalize_path(os.path.join(score_path, audio_file))}.mp3"
                audio_doc = audios_by_path.get(audio_path, None)

                if audio_doc is None:
                    with open(log_file, "a", encoding="utf-8") as log_f:
                        log_f.write(f"Audio {audio_path} not found in JSON database\n")
                    continue

                instrument_ids = audio_doc.get("instruments", [])
                instrument_ids = [id_["$oid"] for id_ in instrument_ids]
                instrument_names = [instruments_by_id[i]["name"] for i in instrument_ids if i in instruments_by_id]

                if not instrument_names:
                    with open(log_file, "a", encoding="utf-8") as log_f:
                        log_f.write(f"No instruments found for audio {audio_path}\n")
                    continue

                # ---- write metadata ----
                metadata = {
                    "title": score_title,
                    "composer": composer_name,
                    "instruments": instrument_names,
                    "cuts": cuts
                }

                
                if os.path.exists(metadata_file):
                    print(f"Metadata file {metadata_file} was already created.")
                else:
                    with open(metadata_file, "w", encoding="utf-8") as f:
                        json.dump(metadata, f, indent=4)        

                print(f"Metadata saved to {metadata_file}")

    # ---- Save files.lst ----
    all_files = [normalize_path(f) for f in all_files if check_modalities_file(ds_dir, f, log_dir=log_dir)]
    with open(os.path.join(ds_dir, "files.lst"), "w", encoding="utf-8") as f:
        f.write("\n".join(all_files))

    print("All files saved to files.lst")

    return all_files

def copy_precomputed_partitions(ds_dir, partition_folder="partitions"):
    dst = os.path.join(ds_dir, partition_folder)
    if os.path.exists(partition_folder):
        if os.path.exists(dst):
            print(f"Partition directory {dst} already exists. Skipping copy.")
        else:
            shutil.copytree(partition_folder, dst)
            print(f"Copied pre-computed partitions from {partition_folder} to {dst}")
    else:
        print(f"No pre-computed partitions found at {partition_folder}.")
