from setuptools import setup


setup(
    name='cryptocurrency-quotes',
    version='1.0',
    packages=['app', 'app.views', 'app.models', 'app.controllers', 'stock_chart'],
    url='https://github.com/WtCrow/client_cryptocurrency_quotes',
    license='',
    author='Babenko Denis',
    author_email='babenko.denis3009@gmail.com',
    description='Client for project from this link: https://github.com/WtCrow/cryptocurrency_quotes',
    install_requires=['pyqtgraph==0.10.0', 'numpy==1.16.2', 'aiohttp==3.5.4', 'PyQt5==5.13.1']
)
