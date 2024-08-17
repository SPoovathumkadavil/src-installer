import json
import os
from typing import Optional
import boilerutils
from coloring import Color, colorize

def get_default_build_instruction(method: str):
    if method == "autoconf":
        return json.load(open(os.path.join(boilerutils.BUILD_INSTRUCTION_DIR, "default_autoconf.json"), 'r'))

def validate_chunk_info(name: str, info: dict) -> None:
    if "name" not in info:
        raise ValueError("name not defined in formula: "+name)
    if "dependencies" not in info:
        raise ValueError("dependencies not defined in formula: "+name)
    if "method" not in info:
        raise ValueError("method not defined in formula: "+name)
    if info["method"] == "autoconf":
        if "link" not in info:
            raise ValueError("link not defined in formula "+name)

class BuildInfo:
    def __init__(self, chunk_info: dict, prefix: str, target: str):
        self.chunk_info = chunk_info
        self.prefix = prefix
        self.target = target


class Chunk:
    def __init__(self, name: str, method: dict, info: BuildInfo):
        self.name = name
        self.method = method
        self.info = info

    def resolve_method(self) -> None:
        for step in self.method:
            for i in range(len(self.method[step])):
                if "[[name]]" in self.method[step][i]:
                    self.method[step][i] = self.method[step][i].replace(
                        "[[name]]", self.info.chunk_info["name"]
                    )
                if "[[prefix]]" in self.method[step][i]:
                    self.method[step][i] = self.method[step][i].replace("[[prefix]]", self.info.prefix)
                if "[[target]]" in self.method[step][i]:
                    self.method[step][i] = self.method[step][i].replace("[[target]]", self.info.target)
                if "[[tmp]]" in self.method[step][i]:
                    self.method[step][i] = self.method[step][i].replace("[[tmp]]", boilerutils.TMP_DIR)
    
    def override(self, key: str, value: list) -> None:
        if key in self.method:
            self.method[key] = value
    
    def add_configure_flag(self, flag: str) -> None:
        self.method["configure"][0] += " " + flag
    
    def to_build(self, check_exists: bool) -> str:
        self.resolve_method()
        s_bs=""
        if check_exists:
            s_bs += "if [ ! -f "+os.path.join(boilerutils.PREFIX, "bin", self.name)+" ]; then\n\t"
        s_bs += "echo \"installing "+self.name+"\"\n"
        for step in self.method:
            for i in range(len(self.method[step])):
                if check_exists:
                    s_bs+="\t"
                s_bs+=self.method[step][i]
                s_bs+="\n"
        if check_exists:
            s_bs+="fi"
        return s_bs
    
    def find_formula(self) -> Optional[dict]:
        p = os.path.join(boilerutils.FORMULA_DIR, self.name + ".json")
        if os.path.exists(p):
            return json.load(open(p, 'r'))
        return None
