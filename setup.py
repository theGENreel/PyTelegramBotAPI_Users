from setuptools import setup, find_packages


def read(filename):
    with open(filename, encoding='utf-8') as file:
        return file.read()


setup(
    name='PyTelegramBotApi_Users',
    version='1.0',
    description='User access manager for async pyTelegramBotAPI',
    long_description=read('README.md'),
    long_description_content_type='text/markdown',
    author='skummer',
    author_email='thegenreel@gmail.com',
    url='https://github.com/theGENreel/PyTelegramBotAPI_Users',
    packages=find_packages(),
    license='GPL3',
    install_requires=['pytelegrambotapi', 'aiofiles']
)
