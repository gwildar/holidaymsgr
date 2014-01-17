from setuptools import setup, find_packages

version = '0.9.dev0'

setup(
    name='holidaymsgr',
    version=version,
    packages=find_packages(exclude=['ez_setup']),
    package_data={'holidaymsgr': ['stack_templates/apache/holidaymsgr.conf', 'stack_templates/upstart/holidaymsgr.conf']},
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


