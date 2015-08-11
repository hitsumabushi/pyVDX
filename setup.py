from io import open
from setuptools import setup, find_packages

long_description = open('README.md', 'r', encoding='utf8').read()

setup(
    name='pyVDX',
    version='0.1',
    description='Python tool for manage Brocade VDX switches',
    long_description=long_description,
    author='Kohei Sakai',
    author_email='053023.math@gmail.com',
    license='MIT',
    packages=find_packages(exclude=['ez_setup']),
    # tests_require=['nose'],
    # test_suite='nose.collector',
    url='http://github.com/hitsumabushi/pyVDX',
    include_package_data=True,
    classifiers=[
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4'],
    keywords=['Brocade', 'VDX', 'network']
)
