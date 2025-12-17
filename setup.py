from distutils.core import setup
import py2exe

setup(
    name="Ordem e Ajuste",
    version="1.0",
    description="Automacao Ordem e Ajuste",
    scripts=["launcher.py"],
    options={
        "py2exe": {
            "bundle_files": 1,
            "compressed": True,
            "includes": ["requests"]
        }
    }
)

