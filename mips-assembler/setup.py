from setuptools import setup, find_packages

setup(
    name="mips-assembler",
    version="1.0",
    packages=find_packages(),
    install_requires=[],
    entry_points={
        'console_scripts': [
            'mips-assembler=mips_assembler.cli:main',
        ],
    },
    author="Your Name",
    author_email="your.email@example.com",
    description="A MIPS assembler written in Python",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/mips-assembler",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
) 