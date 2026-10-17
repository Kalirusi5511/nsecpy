import setuptools


with open("readme.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="nsecpy",
    version="0.2.0",
    author="Kalirusi5511",
    description="A Nintendo Switch eShop API wrapper",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.9',
    install_requires=[
        "aiohttp>=3.8,<3.11",
        "dateparser>=1.1.0",
    ],
)
