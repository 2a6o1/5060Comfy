from setuptools import setup, find_packages
import sys

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Leer requirements.txt
def parse_requirements(filename):
    with open(filename, "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

requirements = parse_requirements("requirements.txt")

setup(
    name="comfyui-manager",
    version="1.0.0",
    author="Tu Nombre",
    author_email="tu@email.com",
    description="GUI Manager for ComfyUI with system monitoring and optimizations",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tuusuario/comfyui-manager",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Multimedia :: Graphics",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "comfyui-manager=comfyui_manager.main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "comfyui_manager": ["assets/*", "assets/icons/*", "assets/themes/*"],
    },
    project_urls={
        "Bug Reports": "https://github.com/tuusuario/comfyui-manager/issues",
        "Source": "https://github.com/tuusuario/comfyui-manager",
    },
)