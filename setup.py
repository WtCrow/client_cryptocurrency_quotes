from setuptools import setup


setup(
    name='cryptocurrency-quotes',
    version='1.0',
    packages=['app', 'app.views', 'app.models', 'app.controllers', 'app.models.chart_item'],
    license='',
    author='Babenko Denis',
    author_email='babenko.denis3009@gmail.com',
    url='https://github.com/WtCrow/client_cryptocurrency_quotes',
    description='Client for project from this link: https://github.com/WtCrow/cryptocurrency_quotes',
    install_requires=['pyqtgraph==0.11.0', 'numpy==1.19.1', 'aiohttp==3.8.5', 'PyQt5==5.15.0']
)
