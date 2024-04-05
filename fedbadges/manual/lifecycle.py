import datetime
import logging

import click
import fasjson_client
from fedora_messaging.config import conf as fm_config
from tahrir_api.dbapi import TahrirDatabase

import fedbadges.utils

from .utils import award_badge, option_debug, setup_logging


log = logging.getLogger(__name__)


def get_fas_userlist(fasjson, threshold):
    # Users in the fedora-contributor group are members of at least 1 group.
    search_terms = dict(group="fedora-contributor", creation__before=threshold.isoformat())
    page_number = 0
    next_page_exists = True
    while next_page_exists:
        page_number += 1
        response = fasjson.search(
            page_size=40,
            page_number=page_number,
            _request_options={"headers": {"X-Fields": "username"}},
            **search_terms
        )
        yield from response.result
        next_page_exists = page_number < response.page["total_pages"]


@click.command()
@option_debug
def main(debug):
    setup_logging(debug=debug)
    config = fm_config["consumer_config"]
    uri = config["database_uri"]
    tahrir = TahrirDatabase(
        uri,
        notification_callback=fedbadges.utils.notification_callback,
    )
    badge = tahrir.get_badge(badge_id="badge-off!")
    if not badge:
        raise ValueError("badge does not exist")

    fasjson = fasjson_client.Client(config["fasjson_base_url"])

    now = datetime.datetime.now(tz=datetime.timezone.utc)
    year = datetime.timedelta(days=365.5)
    mapping = {
        "egg": year * 1,
        "embryo": year * 2,
        "tadpole": year * 3,
        "tadpole-with-legs": year * 5,
        "froglet": year * 7,
        "adult-frog": year * 10,
    }

    # Query IPA for users created before the threshold
    for badge_id, delta in list(mapping.items()):
        badge = tahrir.get_badge(badge_id=badge_id)
        if not badge.id:
            log.error("Badge %s does not exist", badge_id)
            continue
        threshold = now - delta
        for person in get_fas_userlist(fasjson, threshold):
            email = person["username"] + "@fedoraproject.org"
            award_badge(tahrir, badge, email)


if __name__ == "__main__":
    main()
