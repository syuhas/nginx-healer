from setuptools import setup, find_packages

setup(
    name='webhook-healer-api',
    version='0.2.0',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'runserver=run_uvicorn:run'
        ]
    },
    install_requires=[
        'fastapi',
        'uvicorn',
        'loguru'
    ],
    extras_require={
        'dev': ['pytest', 'pytest-cov']
    }
)