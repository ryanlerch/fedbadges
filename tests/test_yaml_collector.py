import unittest

import tahrir_api.dbapi
import fedbadges.consumers

from mock import patch
from nose.tools import eq_


class MockHub(object):
    config = {
        "fedmsg.consumers.badges.enabled": True,
        "badges.yaml.directory": "tests/test_badges",
        "badges_global": {
            "database_uri": "sqlite:////tmp/sqlite.db",
            "badge_issuer": dict(
                issuer_id='Fedora Project',
                issuer_origin='http://badges.fedoraproject.com',
                issuer_name='Fedora Project',
                issuer_org='http://fedoraproject.org',
                issuer_contact='rdelinge@redhat.com'
            ),
        },
    }

    def subscribe(self, topic, callback):
        pass


class TestYamlCollector(unittest.TestCase):

    def setUp(self):
        hub = MockHub()
        with patch.object(tahrir_api.dbapi.TahrirDatabase, 'add_issuer'):
            self.consumer = fedbadges.consumers.FedoraBadgesConsumer(hub)

    def test_load_badges_number(self):
        """ Determine that we can load badges from file. """
        eq_(len(self.consumer.badges), 2)

    def test_load_badges_contents(self):
        """ Determine that we can load badges from file. """
        names = set([badge['name'] for badge in self.consumer.badges])
        eq_(names, set([
            'Like a Rock',
            'The Zen of Foo Bar Baz',
            ]))
