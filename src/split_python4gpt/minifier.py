#!/usr/bin/env python3.10

import contextlib
import shutil
import subprocess
from pathlib import Path

from python_minifier import minify
from pytype.tools.merge_pyi import merge_pyi


class PyTypingMinifier:
    def __init__(self, py_ver="3.10"):
        self.PY_TYPE_PY_VER = py_ver
        self.PY_TYPE_PY_EXE = shutil.which(f"python{self.PY_TYPE_PY_VER}")
        self.py_folder = None
        self.out_py_folder = None
        self.pyi_folder = None
        self.py_path = None
        self.out_py_path = None
        self.pyi_path = None
        self.py_code = None
        self.code_data = {
            "py_path": Path(),
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
        out_py_path.parent.mkdir(parents=True, exist_ok=True)
        if out_py_path != py_path:
            shutil.copy2(py_path, out_py_path)
        pyi_path = Path(
            self.pyi_folder, ".pytype", "pyi", out_py_path.with_suffix(".pyi").name
        )
        py_code = out_py_path.read_text()
        code_data = {
            "py_path": py_path,
            "pyi_path": pyi_path,
            "py_code": py_code,
        }
        return out_py_path, code_data

    def infer_types(
        self, py_path: str | Path, pyi_path: str | Path, py_code: str
    ) -> str:
        with contextlib.suppress(subprocess.CalledProcessError):
            command = [
                self.PY_TYPE_PY_EXE,
                "-m",
                "pytype",
                f"--python-version={self.PY_TYPE_PY_VER}",
                str(py_path),
            ]
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
            if types:
                py_code = self.infer_types(
                    out_py_path, code_data["pyi_path"], code_data["py_code"]
                )
            if mini:
                py_code = self.minify(py_code, **minify_options)
            code_data["py_code"] = py_code
            out_py_path.write_text(py_code)
        return list(self.code_folder_data.keys())
