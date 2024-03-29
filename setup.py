import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="rstx",
    version="0.4.1",
    author="tantanGH",
    author_email="tantanGH@github",
    license='MIT',
    description="RS232C Binary File Transfer Tool in Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tantanGH/rstx",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={
        'console_scripts': [
            'rstx=rstx.rstx:main'
        ]
    },
    packages=setuptools.find_packages(),
    python_requires=">=3.7",
    setup_requires=["setuptools"],
    install_requires=["pyserial"],
)
