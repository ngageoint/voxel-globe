import sys

from django.core.management.commands.loaddata import Command as LoadDataCommand

#https://gist.github.com/bmispelon/ad5a2c333443b3a1d051
class Command(LoadDataCommand):
    def parse_name(self, fixture_name):
        self.compression_formats['stdin'] = (lambda x,y: sys.stdin, None)
        if fixture_name == '-':
            return '-', 'json', 'stdin'

    def find_fixtures(self, fixture_label):
        if fixture_label == '-':
            return [('-', None, '-')]
        return super(Command, self).find_fixtures(fixture_label)