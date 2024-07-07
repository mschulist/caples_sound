import setuptools

REQUIREMENTS = ["chirp @ git+https://github.com/google-research/perch.git"]

setuptools.setup(
    name="gather-target-recordings",
    version="0.1",
    packages=setuptools.find_packages(),
    install_requires=REQUIREMENTS,
)
