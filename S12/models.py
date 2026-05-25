from peewee import *

db = SqliteDatabase('S12.db')


class BaseModel(Model):
    class Meta:
        database = db


class AssessmentForm:
    EXAM = 'exam'
    CREDIT = 'credit'


class Specialization(BaseModel):
    code = CharField(primary_key=True, max_length=20)
    name = CharField(max_length=255)
    duration_training = IntegerField()
    is_active = BooleanField(default=True)

    class Meta:
        table_name = 'specializations'


class Group(BaseModel):
    number = IntegerField()
    prefix = CharField(max_length=10)
    year_create = IntegerField()
    status = CharField(max_length=20, default='active')
    specialization = ForeignKeyField(Specialization, backref='groups', column_name='specialization_code')

    class Meta:
        table_name = 'groups'
        constraints = [SQL('UNIQUE(number, prefix, year_create)')]


class Discipline(BaseModel):
    name = CharField(max_length=255, unique=True)
    is_active = BooleanField(default=True)

    class Meta:
        table_name = 'disciplines'


class Semester(BaseModel):
    semester_number = IntegerField()
    academic_year = CharField(max_length=9)

    class Meta:
        table_name = 'semesters'
        constraints = [SQL('UNIQUE(semester_number, academic_year)')]


class Curriculum(BaseModel):
    """Учебный план (транзитивная таблица)"""
    group = ForeignKeyField(Group, backref='curriculum_records')
    discipline = ForeignKeyField(Discipline, backref='curriculum_records')
    semester_number = IntegerField()
    theory_hours = IntegerField()
    practice_hours = IntegerField()
    assessment_form = CharField(max_length=10)
    is_active = BooleanField(default=True)

    class Meta:
        table_name = 'curriculum'
        constraints = [
            SQL('UNIQUE(group_id, discipline_id, semester_number)'),
            SQL('CHECK(semester_number BETWEEN 1 AND 8)'),
            SQL('CHECK(theory_hours >= 0)'),
            SQL('CHECK(practice_hours >= 0)'),
            SQL("CHECK(assessment_form IN ('exam', 'credit'))")
        ]


def create_tables():
    db.create_tables([Specialization, Group, Discipline, Semester, Curriculum])


def add_default_data():
    default_specializations = [
        ('09.02.07', 'Информационные системы и программирование', 4),
        ('09.02.01', 'Компьютерные системы и комплексы', 4),
    ]
    for code, name, duration in default_specializations:
        Specialization.get_or_create(code=code, defaults={'name': name, 'duration_training': duration})

    if Semester.select().count() == 0:
        for year in range(2024, 2027):
            for sem in range(1, 9):
                Semester.create(semester_number=sem, academic_year=f"{year}-{year+1}")
        print("✓ Семестры добавлены")


if __name__ == '__main__':
    create_tables()
    add_default_data()
