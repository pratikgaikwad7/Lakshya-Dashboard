"""Initialize or migrate all application tables in dependency order."""

from models.evaluations.schema import init_evaluation_db
from models.students.schema import init_db as init_student_db
from models.user_model import init_user_db


def main():
    init_student_db()
    init_evaluation_db()
    init_user_db()
    print("Lakshya Dashboard database tables are ready.")


if __name__ == "__main__":
    main()
