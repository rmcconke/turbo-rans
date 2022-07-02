import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="turborans",
    version="1.0.0",
    author="rmcconke",
    author_email="rmcconke@uwaterloo.ca",
    description="turborans: optimization of turbulence model coefficients",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/rmcconke/turbo-rans",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)