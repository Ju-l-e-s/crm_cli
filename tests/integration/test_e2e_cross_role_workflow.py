import os
import re

import pexpect
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session as FileSession

from models.base import Base
from models.user import User
from tests.conftest import APP_CMD, login, nav_main, extract_id


@pytest.mark.integration
def test_full_cli_flow(tmp_path, setup_test_users):
    # 0) Disable ANSI and configure temp DB
    os.environ["NO_COLOR"] = "1"
    os.environ["RICH_NO_COLOR"] = "1"
    db_path = tmp_path / "test.db"
    os.environ["DATABASE_URL"] = f"sqlite:///{db_path}"

    # 1) Bootstrap schema + seed users
    engine = create_engine(os.environ["DATABASE_URL"], echo=False)
    Base.metadata.create_all(engine)
    with FileSession(engine) as fs:
        for u in setup_test_users.values():
            usr = User(fullname=u.fullname, email=u.email, role=u.role)
            usr.set_password("Pwd1234")
            fs.add(usr)
        fs.commit()

    # 2) COMMERCIAL : Create a client
    cli = pexpect.spawn(APP_CMD, env=os.environ, encoding="utf-8", timeout=5)
    login(cli, "bart@simpson.com", "Pwd1234", "Bart Simpson")
    # cli.logfile_read = sys.stdout
    nav_main(cli, "Clients")
    cli.expect("Clients Menu")
    cli.sendline("3") # Add client
    cli.expect("Full name:")
    cli.sendline("Apu Nahasapeemapetilon")
    cli.expect("Email:")
    cli.sendline("apu@kwikemart.com")
    cli.expect("Phone:")
    cli.sendline("+33123456789")
    cli.expect("Company:")
    cli.sendline("Kwik-E-Mart")

    # 3) Extract ID
    cli.expect("Clients Menu")
    client_id = extract_id(cli)

    # 4) Back to Main Menu and logout
    cli.sendline("6")  # Back
    nav_main(cli, "Log out")
    cli.expect("Logout successful")

    cli.close()

    # 5) GESTION : Create a contract
    cli = pexpect.spawn(APP_CMD, env=os.environ, encoding="utf-8", timeout=5)
    login(cli, "skinner@ecole.com", "Pwd1234", "Seymour Skinner")
    nav_main(cli, "Contracts", role="gestion")
    cli.expect("Contracts Menu")
    cli.sendline("2")                    # Add contract
    cli.expect("Client ID:")
    cli.sendline(str(client_id))
    cli.expect("Total amount:")
    cli.sendline("5000")
    cli.expect("y/n")
    cli.sendline("y")
    cli.expect("End date")
    cli.sendline("2026-12-31")
    cli.expect("Contracts Menu")
    contract_id = extract_id(cli)

    cli.sendline("4")  # Back
    nav_main(cli, "Log out", role="gestion")
    cli.expect("Logout successful")

    cli.close()

    # 6) COMMERCIAL : Create an event
    cli = pexpect.spawn(APP_CMD, env=os.environ, encoding="utf-8", timeout=5)
    login(cli, "bart@simpson.com", "Pwd1234", "Bart Simpson")
    nav_main(cli, "Events")
    cli.expect("Events Menu")
    cli.sendline("2")                    # Add event
    cli.expect("Contract ID:")
    cli.sendline(str(contract_id))
    cli.expect("Event name:")
    cli.sendline("Grand Opening")
    cli.expect(re.compile(r"Start.*HH:MM"))
    cli.sendline("2026-03-01 09:00")
    cli.expect(re.compile(r"End\s+.*HH:MM"))
    cli.sendline("2026-03-01 12:00")
    cli.expect("Location:")
    cli.sendline("Springfield")
    cli.expect("Attendees:")
    cli.sendline("100")
    cli.expect("Notes")
    cli.sendline("VIP only")

    cli.expect("Events Menu")
    event_id = extract_id(cli)

    cli.sendline("3")  # Back
    nav_main(cli, "Log out")
    cli.expect("Logout successful")
    cli.close()

    # 7) GESTION : Assign support to the event
    cli = pexpect.spawn(APP_CMD, env=os.environ, encoding="utf-8", timeout=5)
    login(cli, "skinner@ecole.com", "Pwd1234", "Seymour Skinner")
    nav_main(cli, "Events")
    cli.expect("Events Menu")
    cli.sendline("3")                    # Assign support
    cli.expect("Event ID:")
    cli.sendline(str(event_id))
    cli.expect("Support user ID:")
    cli.sendline(str(setup_test_users["support"].id))
    cli.expect("Events Menu")
    cli.sendline("5")  # Back
    nav_main(cli, "Log out", role="gestion")
    cli.expect("Logout successful")
    cli.close()