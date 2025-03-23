from setuptools import setup, find_packages

setup(
    name="cb_backtest",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "pandas>=2.2.3",
        "numpy>=2.0.2",
        "TA-Lib>=0.4.0",
        "quantstats>=0.0.62",
        "openpyxl>=3.0.10",
        "pyarrow>=8.0.0"
    ],
    python_requires=">=3.8",
    description="Convertible Bond Backtest Framework",
    author="Your Name",
    author_email="your.email@example.com",
) 