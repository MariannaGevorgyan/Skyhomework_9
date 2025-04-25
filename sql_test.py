from sqlalchemy import create_engine
from sqlalchemy.sql import text
from sqlalchemy import inspect



db_connection_string = "postgresql://postgres:551@localhost:5432/postgres"
db = create_engine(db_connection_string)

db_data = {
    "source": 'Technology',
    "update_to": 'Botany',
    "rec-id": False
}

def select(connection, query):
    result = connection.execute(text(query))
    rows = result.mappings().all() # getting result like dictionary
    return rows

def select_1_row(connection, query, param):
    sql_statement = text(query)
    result = connection.execute(sql_statement, {"subject_id": param})
    rows = result.mappings().all()
    return rows


def insert_update(connection, query, param):
    sql = text(query)
    result = connection.execute(sql, param)
    connection.commit()
    return result

def delete(connection, query):
    connection.execute(text(query))
    connection.commit()

def test_db_connection():
    inspector = inspect(db)
    table_names = inspector.get_table_names()
    print(table_names)

    assert "subject" in table_names

def test_select():
    connection = db.connect()
    rows = select(connection, "SELECT * FROM subject ORDER BY subject_id")


    print(rows)

    assert rows[1]['subject_id'] == 2
    assert rows[1]['subject_title'] == 'Mathematics'

    connection.close()

def test_select_1_row():
    connection = db.connect()
    query = "SELECT * FROM subject WHERE subject_id = :subject_id"
    param = 1
    rows = select_1_row(connection, query, param)
    print(rows)

    assert len(rows) == 1

    connection.close()


def test_insert():
    connection = db.connect()
    query = "SELECT MAX(subject_id) FROM subject"
    max_id = select(connection, query)[0]
    db_data["rec_id"] = int(max_id["max"]) + 1
    param = {"id": db_data["rec_id"],
             "data": db_data["source"]
    }

    query = "INSERT INTO subject (subject_id, subject_title) VALUES (:id, :data)"
    insert_update(connection, query, param)

    where = db_data["source"]
    query = f"SELECT subject_id FROM subject WHERE subject_title = '{where}'"
    check_insert = select(connection, query)[0]
    assert check_insert["subject_id"] > 0

    connection.close()

def test_update():
    connection = db.connect()
    source_title = db_data["source"]
    query = f"SELECT subject_id FROM subject WHERE subject_title = '{source_title}'"
    id_update = select(connection, query)[0]
    param = {
        'subject_title': db_data["update_to"],
        'subject_id': id_update['subject_id']
    }
    update_query = "UPDATE subject SET subject_title = :subject_title WHERE subject_id = :subject_id"
    insert_update(connection, update_query, param)

    check_query = f"SELECT subject_id FROM subject WHERE subject_title = '{db_data['update_to']}'"
    check_result = select(connection, check_query)
    assert check_result[0]["subject_id"] > 0

    connection.close()



def test_delete():
    connection = db.connect()
    id_to_del = db_data["source"]
    print(id_to_del)
    delete(connection, f"DELETE FROM subject WHERE subject_title = '{id_to_del}'")

    where = db_data["source"]
    query = f"SELECT subject_id FROM subject WHERE subject_title = '{where}'"


    check_insert = select(connection, query)
    assert check_insert == []

    connection.close()