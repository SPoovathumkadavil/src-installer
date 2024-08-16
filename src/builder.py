# the idea is to gather all the information about the formulas into one (from no deps to final dep)
# into a single script file. Then run the file.

import json
import os
import shutil
import tarfile
import boilerutils
import build_chunk
import requests
from coloring import colorize, Color
import subprocess

def download_to_file(file_name: str, link: str):
    if os.path.exists(boilerutils.TMP_DIR) is False:
        os.mkdir(boilerutils.TMP_DIR)
    with requests.get(link, stream=True) as r:
        r.raise_for_status()
        with open(os.path.join(boilerutils.TMP_DIR, file_name), "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)

def untar(file_name: str):
    # if tarfile.is_tarfile(file_path):
    #     print(f"Cannot untar a non-tar file {file_path}")
    #     return
    extract_dir = boilerutils.TMP_DIR
    d_name = os.path.join(boilerutils.TMP_DIR, file_name[:file_name.find(".tar")])
    if os.path.exists(d_name):
        shutil.rmtree(d_name)
    with tarfile.open(os.path.join(boilerutils.TMP_DIR, file_name), "r") as f:
        f.extractall(extract_dir)

def run_command(command: list):
    c = subprocess.run(command)
    c.check_returncode()

def remove(file_name: str):
    os.remove(os.path.join(boilerutils.TMP_DIR, file_name))

def download_handler(info: dict):
    if info["method"] == "autoconf":
        link = info["link"]
        if "[[name]]" in link:
            link = link.replace("[[name]]", info["name"])
        download_to_file(info["name"]+".tar", link)
        untar(info["name"]+".tar")
        remove(info["name"]+".tar")
    else:
        raise ValueError("unknown build method for "+info["name"])


def sort_deps(r: str, t: str, n: list):
    if t in n:
        return n

    # open target file
    with open(os.path.join(boilerutils.FORMULA_DIR, r, t + ".json"), 'r') as f:
        info = json.load(f)
        if info["dependencies"] == []:
            n.append(t)
        else:
            for i in info["dependencies"]:
                sort_deps(r, i, n)
            n.append(t)
    return n

class Builder:
    def __init__(self, target: str) -> None:
        self.target = target

        # the target is the directory, load files
        self.target_files = os.listdir(os.path.join(boilerutils.FORMULA_DIR, self.target))
        self.build_order = []
        for i in self.target_files:
            check = i.replace(".json", "")
            self.build_order = sort_deps(self.target, check, self.build_order)
    
    def load_build(self):
        self.chunks: list[build_chunk.Chunk] = []
        for i in self.build_order:
            # load json
            try:
                chunk_info = json.load(open(os.path.join(boilerutils.FORMULA_DIR, self.target, i+".json")))
                build_chunk.validate_chunk_info(i, chunk_info)
                method = None
                if chunk_info["method"] == "autoconf":
                    method=build_chunk.get_default_build_instruction("autoconf")
                chunk = build_chunk.Chunk(i, method, build_chunk.BuildInfo(chunk_info, boilerutils.PREFIX, self.target))
                # adds and overrides
                if "override" in chunk_info:
                    for i in chunk_info["override"]:
                        chunk.override(i, chunk_info["override"][i])
                if "add-configure" in chunk_info:
                    for i in chunk_info["add-configure"]:
                        chunk.add_configure_flag(i)
                self.chunks.append(chunk)
                print(colorize(f"{chunk.name} loaded successfully !", Color.GREEN))
            except Exception as e:
                print(colorize("failed to load build for \""+i+"\"", Color.RED))
                print(colorize("Error: " + repr(e), Color.RED))
                return
    
    def download_source(self):
        for i in self.chunks:
            f = i.find_formula()
            if f is not None:
                print(colorize("downloading "+i.info.chunk_info["name"], Color.CYAN))
                download_handler(f)
            else:
                print(colorize("unable to download", i.name, "due to unfindable formula", Color.RED))
                return
        print(colorize("download successful !", Color.GREEN))
    
    def create_build_script(self):
        scr = []
        for i in self.chunks:
            scr.append(i.to_build())
        build_script = "\n".join(scr)
        self.build_file = os.path.join(boilerutils.TMP_DIR, "build_"+self.target+".sh")
        if os.path.exists(self.build_file):
            os.remove(self.build_file)
            print("removed")
        with open(self.build_file, 'w') as f:
            print(build_script, file=f)
        print(colorize("build script created !", Color.GREEN))
        if scr == []:
            print(colorize("build script empty ...", Color.YELLOW))

    def run_build_script(self):
        try:
            run_command(["sh", self.build_file])
        except Exception as e:
            print(colorize("error running build script.", Color.RED))
            print(colorize("error: "+repr(e), Color.RED))

if __name__ == "__main__":
    test_builder = Builder("x86_64-elf")
    print("build order:", test_builder.build_order)
    test_builder.load_build()
    print("chunks:", "true" if test_builder.chunks != [] else "false")
    # test_builder.download_source()
    print("download:", "true" if os.listdir(boilerutils.TMP_DIR) != [] else "false")
    build_script = test_builder.create_build_script()
    print("done")
    test_builder.run_build_script()
