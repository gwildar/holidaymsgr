from setuptools import setup, find_packages

version = '0.4'

setup(
    name='holidaymsgr',
    version=version,
    packages=find_packages(exclude=['ez_setup']),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'Django',
        'Jinja2',
        'gunicorn',
    ],
    entry_points = """
    [console_scripts]
    django = holidaymsgr.scripts.manage:main
    """
    )


