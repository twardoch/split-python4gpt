#!/usr/bin/env python3.10

import logging
import shutil
import subprocess
from pathlib import Path

from python_minifier import minify
from pytype.tools.merge_pyi import merge_pyi


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
        # print(f"[DEBUG] infer_types: py_path='{py_path}', pyi_path='{pyi_path}'", flush=True) # DEBUG
        # print(f"[DEBUG] infer_types: PY_TYPE_PY_EXE='{self.PY_TYPE_PY_EXE}'", flush=True) # DEBUG
        if not self.PY_TYPE_PY_EXE:
            logging.error("PY_TYPE_PY_EXE is not set. Cannot run pytype.")
            return py_code

        command = [
            self.PY_TYPE_PY_EXE,
            "-m",
            "pytype",
            f"--python-version={self.PY_TYPE_PY_VER}",
            str(py_path),  # This is the out_py_path, where the copied file resides
        ]
        try:
            # Ensure the .pytype/pyi directory exists for pytype to write into
            # pytype typically creates this, but good to be defensive or if permissions are an issue.
            # However, pytype is run with cwd=self.pyi_folder, so it will create .pytype/pyi relative to that.
            # Path(pyi_path).parent.mkdir(parents=True, exist_ok=True) # pyi_path includes .pytype/pyi

            result = subprocess.run(
                command,
                cwd=self.pyi_folder,  # pytype will output to .pytype/pyi within this cwd
                check=True,
                capture_output=True,  # Capture stdout/stderr
                text=True,
            )
            logging.info(f"Pytype stdout for {py_path}:\n{result.stdout}")
            logging.info(f"Pytype stderr for {py_path}:\n{result.stderr}")

            # If pytype succeeds, the .pyi file should exist at the location pytype creates it.
            # Our pyi_path variable is constructed to match this expected location.
            if Path(pyi_path).exists():
                pyi_code = Path(pyi_path).read_text()
                if pyi_code.strip():  # Check if pyi file is not empty
                    py_code = merge_pyi.merge_sources(py=py_code, pyi=pyi_code)
                else:
                    logging.info(
                        f"Pytype generated an empty .pyi file for {py_path} at {pyi_path}. No types merged."
                    )
            else:
                logging.warning(
                    f"Pytype ran for {py_path} (stdout above), but output .pyi file {pyi_path} not found. Skipping type merging."
                )
        except subprocess.CalledProcessError as e:
            logging.warning(
                f"Pytype failed for {py_path}. Exit code: {e.returncode}. Stderr: {e.stderr}. Stdout: {e.stdout}. Skipping type merging."
            )
        except FileNotFoundError as e:
            # This could happen if PY_TYPE_PY_EXE is not found, or if pyi_path.read_text() fails
            # after a successful pytype run but the file is somehow missing.
            logging.error(
                f"File not found during type inference for {py_path}. Error: {e}. "
                f"Ensure Pytype executable '{self.PY_TYPE_PY_EXE}' is correct and accessible, "
                f"or check pyi file path: {pyi_path}. Skipping type merging."
            )
        except Exception as e:
            # Catch any other unexpected errors during type inference.
            logging.error(
                f"An unexpected error occurred during type inference for {py_path}. Type: {type(e).__name__}, Error: {e}. "
                "Skipping type merging."
            )
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

        processed_file_paths = []
        for out_py_path, file_data in self.code_folder_data.items():
            # Start with the current code for this file
            current_processed_code = file_data["py_code"]

            if types:
                current_processed_code = self.infer_types(
                    out_py_path, file_data["pyi_path"], current_processed_code
                )

            if mini:
                try:
                    current_processed_code = self.minify(
                        current_processed_code, **minify_options
                    )
                except Exception as e:
                    logging.error(
                        f"Minification failed for {out_py_path}. Error: {type(e).__name__}: {e}. Skipping minification for this file."
                    )
                    # current_processed_code remains what it was after type inference (or original if types=False)

            # Update the stored code in code_folder_data and write to the output file
            file_data["py_code"] = current_processed_code
            out_py_path.write_text(current_processed_code)
            processed_file_paths.append(out_py_path)

        return processed_file_paths
