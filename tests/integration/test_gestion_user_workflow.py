import os

import pexpect
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session as DBSession

from models.base import Base
from models.user import User


from tests.conftest import (
    login, nav_main, nav_submenu,
    APP_CMD
)

@pytest.mark.integration
def test_gestion_user_management_workflow(tmp_path, setup_test_users):
    """Test complet de gestion des utilisateurs par un gestionnaire."""
    os.environ["NO_COLOR"] = "1"
    os.environ["RICH_NO_COLOR"] = "1"
    db_path = tmp_path / "testing.db"
    os.environ["DATABASE_URL"] = f"sqlite:///{db_path}"
    timeout = 5

    engine = create_engine(os.environ["DATABASE_URL"], echo=False)
    Base.metadata.create_all(engine)
    
    with DBSession(engine) as db:
        for u in setup_test_users.values():
            usr = User(fullname=u.fullname, email=u.email, role=u.role)
            usr.set_password("Pwd1234")
            db.add(usr)
        db.commit()

    # --- 1) Connection as gestion ---
    cli = pexpect.spawn(APP_CMD, env=os.environ, encoding="utf-8", timeout=timeout)
    login(cli, "skinner@ecole.com", "Pwd1234", "Seymour Skinner")

    # --- 2) Create a new user ---
    nav_main(cli, "Collaborators", role="gestion")
    nav_submenu(cli, "Add user", "2")
    
    # Fill the new user information
    cli.expect("Full name:")
    cli.sendline("Ned Flanders")
    cli.expect("Email:")
    cli.sendline("ned@church.com")
    cli.expect("(commercial/support/gestion)")
    cli.sendline("commercial")
    cli.expect("Password:")
    cli.sendline("IloveChurch<3")
    cli.expect("Confirm password:")
    cli.sendline("IloveChurch<3")
    
    # Get the created user ID
    cli.expect("Created user ID")
    user_id = '4'
    assert user_id is not None
    
    cli.expect("Collaborators Menu")
    
    # --- 3) Edit the user ---
    nav_submenu(cli, "Edit user", "3")  # Edit user
    cli.expect("User ID to edit")
    cli.sendline(str(user_id))
    
    # Edit the user fields
    cli.expect("New full name")
    cli.sendline("") 
    cli.expect("New email")
    cli.sendline("newemail@church.com   ") 
    cli.expect("New role")
    cli.sendline("")
    cli.expect("New password")
    cli.sendline("")
    
    cli.expect("Updated user ID")
    cli.expect("Collaborators Menu")
    
    # --- 4) Verify the modifications ---
    nav_submenu(cli, "List users", "1")  # List all users
    cli.expect("Ned Flanders")  # Verify the new name
    cli.expect("commercial")  # Verify the new role
    cli.sendline("5")  # Quit the list
    
    cli.expect("Main Menu")
    
    # --- 5) Delete the user ---
    cli.sendline("4") # open collaborators menu
    cli.sendline("4") # delete user
    cli.expect("User ID to delete")
    cli.sendline(str(user_id))
    cli.expect("Are you sure")
    cli.sendline("y")  # Confirm the deletion
    cli.expect("Collaborators Menu")  # Attendre que le menu réapparaisse

    output = cli.before
    assert "has been deleted" in output

    # --- 6) Verify the deletion ---
    nav_submenu(cli, "List users", "1")  # List all users
    output = cli.before + cli.after
    assert f"ID {user_id}" not in output
    cli.sendline("5")
    cli.expect("Main Menu")
    # --- 7) Logout ---

    nav_main(cli, "Log out", role="gestion")
    cli.expect("Logout successful")
    cli.close()
    
    # --- 8) Final verification in the database ---
    with DBSession(engine) as db:
        user = db.query(User).filter(User.id == user_id).first()
        assert user is None
