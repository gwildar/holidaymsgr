from setuptools import setup, find_packages

version = '0.5.dev0'

setup(
    name='holidaymsgr',
    version=version,
    packages=find_packages(exclude=['ez_setup']),
    include_package_data=True,
    package_data={'holidaymsgr': ['holidaymsgr/stack_templates']},
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


