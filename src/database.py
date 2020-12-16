import sqlite3, time

creations: list = list()


def getCon(config=None,):
    if not config:
        config: dict = {
            "database": "database.db",
        }

    class abstraction:  # Database class object

        def __init__(self):
            self.connection: sqlite3 = sqlite3.connect(
                config.get(
                    "database"
                ),
            )
            self.connection.row_factory = sqlite3.Row
            self.cursor = self.connection.cursor()

        def close(self):
            self.connection.commit()
            self.cursor.close()
            self.connection.close()

    return abstraction()


def creation(function):
    creations.append(
        function,
    )
    return function


def createTables():
    abstraction = getCon()
    [
        abstraction.cursor.execute(
            create.__doc__
        ) for create in creations
          if create.__doc__
    ]
    abstraction.close()


@creation
def createRolesPersist():
    """
    CREATE TABLE IF NOT EXISTS roles
    (
        userid BIGINT UNSIGNED NOT NULL,
        roleid BIGINT UNSIGNED NOT NULL,
        assignment BIGINT UNSIGNED NOT NULL
    );
    """

@creation
def createTags():
    """
    CREATE TABLE IF NOT EXISTS tags
    (
        uid INT UNSIGNED NOT NULL,
        name BIGTEXT NOT NULL,
        value BIGTEXT NOT NULL
    );
    """

def getuserroles(userid: int):  # Returns a list of users role ids
    """
    SELECT *
    FROM roles
    WHERE userid = ?
    """
    con = getCon()
    data = con.cursor.execute(getuserroles.__doc__, (userid,)).fetchall()
    con.close()
    return [dict(userobject).get("roleid") for userobject in data]


def setuserrole(userid, roles: (list, int)):  # sets a users role or list of roles
    """
    INSERT INTO
    roles (
        userid,
        roleid,
        assignment
    ) VALUES (?,?,?);
    """
    timestamp = round(time.time())
    con = getCon()
    if type(roles) == int:
        con.cursor.execute(setuserrole.__doc__, (userid, roles, timestamp))
        con.close()
    elif type(roles) == list:
        [con.cursor.execute(setuserrole.__doc__, (userid, role, timestamp)) for role in roles if type(role) == int]
        con.close()
    else:
        con.close()
        raise Exception("roles argument must be integer or a list of integers")


def getTag(name: str) -> list:
    """
    SELECT *
    FROM tags
    WHERE name LIKE ?;
    """
    con = getCon()
    data = con.cursor.execute(getTag.__doc__, (name,)).fetchall()
    con.close()
    return [dict(value).get("value") for value in data]


def makeTag(name: str, value: str, author: int) -> list:
    """
    INSERT INTO
    tags (
        uid,
        name,
        value
    ) VALUES (?,?,?);
    """

    con = getCon()
    exists = getTag(name)
    if not exists:
        con.cursor.execute(makeTag.__doc__, (author, name, value))
        con.close()
        return getTag(name)
    else:
        raise Exception(f"{name} already exists")


def deleteTag(name: str) -> str:
    """
    DELETE FROM tags
    WHERE name = ?;
    """
    con = getCon()
    exists = getTag(name)
    if not exists:
        raise Exception(f"Tag {name} doesn't exist")
    else:
        con.cursor.execute(deleteTag.__doc__, (name,))
        con.close()
        return f"Tag {name} has been deleted"

def editTag(name: str, value: str, author: int):
    """
    UPDATE tags
    SET uid = ?, name = ?, value = ?
    WHERE name = ?
    """
    con = getCon()
    try:
        response = con.cursor.execute(
            editTag.__doc__,
            (author, name, value, name)
            )
        return response
    except Exception as e:
        raise e
