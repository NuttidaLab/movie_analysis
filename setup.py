from setuptools import setup, find_packages
# read the long description from README.md
here = Path(__file__).parent
long_description = (here / "README.md").read_text(encoding="utf-8")

def load_requirements(fname):
    with open(fname) as f:
        return [line.strip() for line in f
                if line.strip() and not line.startswith("#")]

setup(
    name="Naturalistic",
    version="0.1.0",
    author="Siddhant Iyer",
    author_email="si2442@cumc.columbia.edu",
    description="Code for Naturalistic Movie Analysis",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(exclude=["analysis", "analysis.*"]),
    python_requires=">=3.12",
    install_requires=load_requirements("requirements.txt"),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    entry_points={},
)