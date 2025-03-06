#!/usr/bin/env python3.10

import logging
import shutil
import subprocess
from ast import ClassDef, FunctionDef, NodeTransformer, fix_missing_locations, parse
from os import environ
from pathlib import Path

import tiktoken
from astor import to_source
from python_minifier import minify
from pytype.tools.merge_pyi import merge_pyi
from simpleaichat import AIChat

OPENAI_MODELS = {
    "gpt-4": 8192,
    "gpt-4-32k": 32768,
    "gpt-4-32k-0613": 32768,
    "gpt-4-0613": 8192,
    "gpt-3.5-turbo": 4096,
    "gpt-3.5-turbo-0613": 4096,
    "gpt-3.5-turbo-16k": 16384,
    "gpt-3.5-turbo-16k-0613": 16384,
}


class PyTypingMinifier:
    def __init__(self, py_ver="3.10"):
        self.PY_TYPE_PY_VER = py_ver
        self.PY_TYPE_PY_EXE = shutil.which(f"python{self.PY_TYPE_PY_VER}")
        if not self.PY_TYPE_PY_EXE:
            logging.warning(
                f"Python executable for version {self.PY_TYPE_PY_VER} not found. "
                "Type inference with Pytype will likely fail."
            )
        # print(f"[DEBUG] PyTypingMinifier.__init__: PY_TYPE_PY_EXE = {self.PY_TYPE_PY_EXE}", flush=True) # DEBUG
        self.py_folder = None
        self.out_py_folder = None
        self.pyi_folder = None
        # self.code_data is a template for data stored in self.code_folder_data
        # It's not strictly needed as an instance variable but harmless.
        self.code_data = {
            "py_path": Path(),
            "rel_path": Path(),
            "pyi_path": Path(),
            "py_code": "",
        }
        self.code_folder_data = {}

    def init_folders(
        self,
        py_folder: str | Path,
        out_py_folder: str | Path | None = None,
        pyi_folder: str | Path | None = None,
    ):
        self.py_folder = Path(py_folder).resolve()
        self.out_py_folder = (
            Path(out_py_folder).resolve() if out_py_folder else self.py_folder
        )
        self.out_py_folder.mkdir(parents=True, exist_ok=True)
        self.pyi_folder = Path(pyi_folder) if pyi_folder else self.out_py_folder
        self.pyi_folder.mkdir(parents=True, exist_ok=True)

    def read_py_file(
        self,
        py_path: str | Path,
        out_py_folder: str | Path | None = None,
        pyi_folder: str | Path | None = None,
    ):
        py_path = Path(py_path).resolve()
        self.init_folders(py_path.parent, out_py_folder, pyi_folder)
        out_py_path, code_data = self.init_code_data(py_path)
        self.code_folder_data[out_py_path] = code_data

    def read_py_folder(
        self,
        py_folder: str | Path,
        out_py_folder: str | Path | None = None,
        pyi_folder: str | Path | None = None,
    ):
        self.init_folders(py_folder, out_py_folder, pyi_folder)
        for py_path in Path(self.py_folder).rglob("*.py"):
            out_py_path, code_data = self.init_code_data(py_path)
            self.code_folder_data[out_py_path] = code_data

    def init_code_data(
        self,
        py_path: str | Path,
    ):
        py_path = Path(py_path).resolve()
        rel_py_path = Path(py_path).relative_to(self.py_folder)
        out_py_path = Path(self.out_py_folder, rel_py_path)
        rel_out_py_path = Path(out_py_path).relative_to(self.out_py_folder)
        out_py_path.parent.mkdir(parents=True, exist_ok=True)
        if out_py_path != py_path:
            shutil.copy2(py_path, out_py_path)
        pyi_path = Path(
            self.pyi_folder, ".pytype", "pyi", rel_out_py_path.with_suffix(".pyi").name
        )
        print(f"{pyi_path=}")
        py_code = out_py_path.read_text()
        code_data = {
            "py_path": py_path,
            "rel_path": rel_py_path,
            "pyi_path": pyi_path,
            "py_code": py_code,
        }
        return out_py_path, code_data

    def infer_types(self, py_path: Path, pyi_path: Path, py_code: str) -> str:
        with contextlib.suppress(subprocess.CalledProcessError):
            command = [
                self.PY_TYPE_PY_EXE,
                "-m",
                "pytype",
                f"--python-version={self.PY_TYPE_PY_VER}",
                str(py_path.relative_to(self.pyi_folder)),
            ]
            print(f"{self.pyi_folder=} {py_path=}")
            subprocess.run(command, cwd=self.pyi_folder, check=True)
            pyi_code = Path(pyi_path).read_text()
            py_code = merge_pyi.merge_sources(py=py_code, pyi=pyi_code)
        return py_code

    def minify(self, py_code: str, **custom_minify_options):
        minify_options = {
            "combine_imports": True,
            "convert_posargs_to_args": True,
            "hoist_literals": False,
            "preserve_shebang": False,
            "remove_annotations": False,
            "remove_asserts": True,
            "remove_debug": True,
            "remove_explicit_return_none": True,
            "remove_literal_statements": True,
            "remove_object_base": True,
            "remove_pass": True,
            "rename_globals": False,
            "rename_locals": False,
        } | custom_minify_options
        return minify(py_code, **minify_options)

    def process_py(
        self,
        py_path_or_folder: str | Path,
        out_py_folder: str | Path | None = None,
        pyi_folder: str | Path | None = None,
        types: bool = True,
        mini: bool = True,
        **minify_options,
    ) -> list[Path]:
        py_path_or_folder = Path(py_path_or_folder).resolve()
        if py_path_or_folder.is_dir():
            self.read_py_folder(py_path_or_folder, out_py_folder, pyi_folder)
        elif py_path_or_folder.is_file():
            self.read_py_file(py_path_or_folder, out_py_folder, pyi_folder)
        else:
            return []
        for out_py_path, code_data in self.code_folder_data.items():
            py_code = code_data["py_code"]
            if types:
                py_code = self.infer_types(out_py_path, code_data["pyi_path"], py_code)
            if mini:
                py_code = self.minify(py_code, **minify_options)
            code_data["py_code"] = py_code
            out_py_path.write_text(py_code)
        return list(self.code_folder_data.keys())


class PyBodySummarizer(NodeTransformer):
    def __init__(self, py_llm_splitter):
        self.py_llm_splitter = py_llm_splitter

    def visit_FunctionDef(self, node, code=None):
        node.body = []
        if code:
            with contextlib.suppress(Exception):
                doc = self.py_llm_splitter.llm_summarize(
                    self.py_llm_splitter.minify(code, remove_literal_statements=False)
                )
                node.body.append(parse(f'"""{doc}"""').body[0])
        node.body.append(parse("...").body[0])
        return node

    def visit_ClassDef(self, node):
        for i, body_node in enumerate(node.body):
            if isinstance(body_node, FunctionDef):
                code = to_source(body_node)
                minified_code = self.py_llm_splitter.minify(
                    code, remove_literal_statements=False
                )  # use methods from PyLLMSplitter instance
                size = self.py_llm_splitter.gptok_size(
                    minified_code
                )  # use methods from PyLLMSplitter instance
                if size > self.py_llm_splitter.gptok_threshold:
                    # replace function body with "..."
                    node.body[i] = self.visit_FunctionDef(body_node, minified_code)
        return node


class PyLLMSplitter(PyTypingMinifier):
    def __init__(
        self,
        *args,
        gptok_model="gpt-3.5-turbo",
        gptok_limit=None,
        gptok_threshold=128,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.gptok_model = gptok_model
        self.gptoker = tiktoken.encoding_for_model(gptok_model)
        self.gptok_limit = gptok_limit or OPENAI_MODELS.get(gptok_model, 2048)
        self.gptok_threshold = gptok_threshold
        self.code_summary = {}
        self.llm_summarize = AIChat(
            api_key=environ.get("OPENAI_API_KEY"),
            system="""Write an extremely short, compact description of this Python code, starting with "This class" or "This method" or "This function" """,
            model=self.gptok_model,
        )

    # @lru_cache(maxsize=None)
    def gptok_size(self, text: str) -> int:
        return len(list(self.gptoker.encode(text)))

    def process_py_code(self, py_code):
        tree = parse(py_code)
        sections = []
        body_summary = PyBodySummarizer(self)  # pass in the instance of PyLLMSplitter
        for node in tree.body:
            code = to_source(node)
            minified_code = self.minify(code, remove_literal_statements=False)
            size = self.gptok_size(minified_code)

            if size > self.gptok_threshold and isinstance(
                node, (FunctionDef, ClassDef)
            ):
                # use body_summary instance to transform the node
                node = body_summary.visit(node)
                fix_missing_locations(node)
                minified_code = self.minify(
                    to_source(node), remove_literal_statements=False
                )
                size = self.gptok_size(minified_code)

            sections.append({"py": minified_code, "gptok_size": size})

        return sections

    def process_py(self, *args, **kwargs):
        paths = super().process_py(*args, **kwargs)

        for path in paths:
            code_data = self.code_folder_data[path]
            sections = self.process_py_code(code_data["py_code"])
            code_data["sections"] = sections
            code_data["gptok_size"] = sum(sec["gptok_size"] for sec in sections)

            self.code_summary[str(path)] = code_data

        return paths

    def write_splits(self):
        splits_folder = self.out_py_folder / "split4gpt"
        splits_folder.mkdir(parents=True, exist_ok=True)

        textportions = []
        current_size = 0
        current_portion = []

        for path, code_data in self.code_summary.items():
            current_portion.append(f"# File: {path}\n")
            current_size += self.gptok_size(f"# File: {path}\n")

            for section in code_data["sections"]:
                if current_size + section["gptok_size"] > self.gptok_limit:
                    textportions.append("".join(current_portion))
                    current_portion = []
                    current_size = 0

                current_portion.append(section["py"])
                current_size += section["gptok_size"]

        if current_portion:
            textportions.append("".join(current_portion))
        for i, textportion in enumerate(textportions, start=1):
            print(textportion, file=open(splits_folder / f"split{i}.py", "w"))
