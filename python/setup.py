from setuptools import setup, find_packages

setup(
    name="venv-python",
    version="0.1.0",
    packages=find_packages(where='src'),
    package_dir={"": "src"},
    install_requires=[
        # Add your required packages here
        # Add other dependencies
    ],
    entry_points={
        "console_scripts": [
            "my_project=main:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.11',
)