import os
import re
import sys

import pexpect
import pytest
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import Session as DBSession

from models.base import Base
from models.contract import Contract
from models.user import User, UserRole

from tests.conftest import login, nav_main, nav_submenu, extract_id, APP_CMD


@pytest.mark.integration
def test_commercial_and_gestion_contract_workflow(tmp_path, setup_test_users):
    """Test client creation/edition by commercial, then contrats by gestion, puis listing+edition by commercial."""
    # --- Setup environment ---
    os.environ["NO_COLOR"] = "1"
    os.environ["RICH_NO_COLOR"] = "1"
    db_path = tmp_path / "testing.db"
    os.environ["DATABASE_URL"] = f"sqlite:///{db_path}"
    timeout = 5

    # --- Init DB + seed users ---
    engine = create_engine(os.environ["DATABASE_URL"], echo=False)
    Base.metadata.create_all(engine)
    with DBSession(engine) as db:
        for u in setup_test_users.values():
            usr = User(fullname=u.fullname, email=u.email, role=u.role)
            usr.set_password("Pwd1234")
            db.add(usr)
        db.commit()

    # --- 1) Commercial creates and edits a client ---

    cli = pexpect.spawn(APP_CMD, env=os.environ,
                        encoding="utf-8", timeout=timeout)
    # cli.logfile_read = sys.stdout

    login(cli, "bart@simpson.com", "Pwd1234", "Bart Simpson")

    # Create client
    nav_main(cli, "Clients")
    nav_submenu(cli, "Clients Menu", "3")
    cli.expect("Full name:")
    cli.sendline("Moe Szyslak")
    cli.expect("Email:")
    cli.sendline("moe@moe.com")
    cli.expect("Phone:")
    cli.sendline("0666666666")
    cli.expect("Company:")
    cli.sendline("Moe's")

    cli.expect("Clients Menu")
    client_id = extract_id(cli)

    # Edit client
    cli.sendline("4")  # Edit
    cli.expect("Client ID to edit")
    cli.sendline(str(client_id))
    cli.expect("New full name")
    cli.sendline("")  # keep
    cli.expect("New email")
    cli.sendline("updated@moe.com")
    cli.expect("New phone")
    cli.sendline("")  # keep
    cli.expect("New company")
    cli.sendline("")  # keep
    cli.expect("Updated client ID")
    cli.expect("Clients Menu")

    # we check "My contracts" is empty
    cli.sendline("6")  # Back
    nav_main(cli, "Contracts")
    nav_submenu(cli, "Contracts Menu", "2")
    cli.expect("No contracts found.")

    # Logout commercial
    cli.sendline("6")  # Back
    nav_main(cli, "Log out")
    cli.expect(re.compile(r"(Logout successful|Exiting\. Goodbye!)"))
    cli.close()

    # --- 2) Gestion creates a contract (assigned to the commercial) ---
    cli = pexpect.spawn(APP_CMD, env=os.environ,
                        encoding="utf-8", timeout=timeout)
    # cli.logfile_read = sys.stdout
    login(cli, "skinner@ecole.com", "Pwd1234", "Seymour Skinner")
    nav_main(cli, "Contracts", role="gestion")
    nav_submenu(cli, "Contracts Menu", "2")
    cli.expect("Client ID:")
    cli.sendline(str(client_id))
    cli.expect("Total amount:")
    cli.sendline("5000")
    cli.expect("y/n")
    cli.sendline("y")
    cli.expect("End date")
    cli.sendline((datetime.now()+timedelta(days=30)).strftime("%Y-%m-%d"))
    contract_id = extract_id(cli)
    cli.sendline("4")  # Back

    # Logout gestion
    nav_main(cli, "Log out", role="gestion")
    cli.expect(re.compile(r"(Logout successful|Exiting\. Goodbye!)"))
    cli.close()

    # --- 3) Commercial lists & edits his only contract ---
    cli = pexpect.spawn(APP_CMD, env=os.environ,
                        encoding="utf-8", timeout=timeout)
    cli.logfile_read = sys.stdout
    login(cli, "bart@simpson.com", "Pwd1234", "Bart Simpson")

    nav_main(cli, "Contracts")
    # list “My contracts”
    nav_submenu(cli, "Contracts Menu", "2")
    cli.expect("List my contracts")
    # edit
    nav_submenu(cli, "Contracts Menu", "5")
    cli.expect("Contract ID to edit")
    cli.sendline(str(contract_id))
    cli.expect("New total amount")
    cli.sendline("6000")
    cli.expect("New remaining amount")
    cli.sendline("")
    cli.expect("y/n")
    cli.sendline("")
    cli.expect("End date")
    cli.sendline("")

    # verify new amount
    nav_submenu(cli, "Contracts Menu", "2")
    cli.expect("6000")
    cli.sendline("6")  # Back
    # Logout final
    nav_main(cli, "Log out")
    cli.expect("Logout successful")
    cli.close()

    # --- DB assertions ---
    with DBSession(engine) as db2:
        contract = db2.get(Contract, contract_id)
        assert contract.total_amount == 6000
