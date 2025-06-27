from setuptools import setup, find_packages

setup(
    name='teng-data-processor',
    version='1.0.0',
    description='A GUI-based signal processing tool for TENG voltage data',
    author='waytohill',
    author_email='your_email@example.com',
    url='https://github.com/waytohill/TENG-data-processor',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'numpy',
        'scipy',
        'matplotlib',
        'pywt',
        'pandas',
    ],
    entry_points={
        'console_scripts': [
            'teng-gui = teng_data_processor.main:main',
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.8',
)