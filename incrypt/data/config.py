import configparser

class Config:
    def __init__(self, section):
        self.config = configparser.ConfigParser()
        self.config.read(r'incrypt/config.ini')
        self.keys = self.config[section]

    def get_section(self, section):
        section = section.upper()
        return self.config[section]