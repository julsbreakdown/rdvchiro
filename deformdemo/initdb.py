import os
import sys
import transaction

from sqlalchemy import engine_from_config
from models import Base

from pyramid.paster import (
    get_appsettings,
    setup_logging,
    )

from models import (
    DBSession,
    Users,
    )


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri>\n'
          '(example: "%s development.ini")' % (cmd, cmd))
    sys.exit(1)


def main(argv=sys.argv):
    print 'called'
    if len(argv) != 2:
        usage(argv)
    config_uri = argv[1]
    setup_logging(config_uri)
    settings = get_appsettings(config_uri)
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.create_all(engine)
    with transaction.manager:
        model =Users(first_name='Julien', last_name='waddle')
        DBSession.add(model)


if __name__ == "__main__":
   main(sys.argv)
