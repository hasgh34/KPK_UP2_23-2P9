from peewee import *
from datetime import datetime

db = SqliteDatabase('curriculum.db')


class BaseModel(Model):
    class Meta:
        database = db


class Group(BaseModel):
    id = AutoField() 
    name = CharField(max_length=100, unique=True, null=False, verbose_name="Название группы")
    created_at = DateTimeField(default=datetime.now, null=False)

    class Meta:
        table_name = 'groups'


class Discipline(BaseModel):
    id = AutoField() 
    name = CharField(max_length=200, unique=True, null=False, verbose_name="Название дисциплины")
    created_at = DateTimeField(default=datetime.now, null=False)

    class Meta:
        table_name = 'disciplines'


class Semester(BaseModel):
    id = AutoField()  
    semester_number = IntegerField(null=False, constraints=[Check('semester_number BETWEEN 1 AND 8')])
    academic_year = CharField(max_length=9, null=False)  # Например, "2024-2025"

    class Meta:
        table_name = 'semesters'
        constraints = [SQL('UNIQUE(semester_number, academic_year)')]


class Curriculum(BaseModel):
    """Учебный план (транзитивная таблица)"""
    id = AutoField()

    group = ForeignKeyField(Group, backref='curriculums', on_delete='CASCADE', null=False)
    discipline = ForeignKeyField(Discipline, backref='curriculums', on_delete='CASCADE', null=False)

    semester_number = IntegerField(
        null=False,
        constraints=[Check('semester_number BETWEEN 1 AND 8')]
    )
    theory_hours = IntegerField(
        null=False,
        constraints=[Check('theory_hours >= 0')]
    )
    practice_hours = IntegerField(
        null=False,
        constraints=[Check('practice_hours >= 0')]
    )
    assessment_form = CharField(
        max_length=10,
        null=False,
        constraints=[Check("assessment_form IN ('exam', 'credit')")]
    )

    is_active = BooleanField(default=True, null=False)

    created_at = DateTimeField(default=datetime.now, null=False)
    updated_at = DateTimeField(default=datetime.now, null=False)

    class Meta:
        table_name = 'curriculum'
        constraints = [SQL('UNIQUE(group_id, discipline_id, semester_number)')]


    @classmethod
    def get_by_id_with_names(cls, record_id):
        try:
            record = cls.get_by_id(record_id)
            return {
                'id': record.id,
                'discipline_id': record.discipline.id,
                'discipline_name': record.discipline.name,
                'group_id': record.group.id,
                'group_name': record.group.name,
                'semester_number': record.semester_number,
                'theory_hours': record.theory_hours,
                'practice_hours': record.practice_hours,
                'assessment_form': record.assessment_form,
                'is_active': record.is_active
            }
        except DoesNotExist:
            return None

    def soft_delete(self):
        if self.is_active:
            self.is_active = False
            self.save()
            return True
        return False

    def update_fields(self, **kwargs):
        forbidden_fields = ['group', 'group_id', 'discipline', 'discipline_id', 'semester_number']

        for field in forbidden_fields:
            if field in kwargs:
                raise ValueError(f"Поле '{field}' нельзя изменить после создания")

        for key, value in kwargs.items():
            if hasattr(self, key) and key in ['theory_hours', 'practice_hours', 'assessment_form']:
                setattr(self, key, value)

        self.updated_at = datetime.now()
        self.save()
        return self

    @classmethod
    def get_filtered_list(cls, filters=None, page=1, page_size=20):
        query = cls.select()

        if filters is None:
            filters = {}

        if 'is_active' not in filters or filters['is_active'] is None:
            query = query.where(cls.is_active == True)

        if filters.get('group_id'):
            query = query.where(cls.group == filters['group_id'])
        if filters.get('discipline_id'):
            query = query.where(cls.discipline == filters['discipline_id'])
        if filters.get('semester_number'):
            query = query.where(cls.semester_number == filters['semester_number'])
        if filters.get('assessment_form'):
            query = query.where(cls.assessment_form == filters['assessment_form'])
        if filters.get('theory_hours_min'):
            query = query.where(cls.theory_hours >= filters['theory_hours_min'])
        if filters.get('theory_hours_max'):
            query = query.where(cls.theory_hours <= filters['theory_hours_max'])
        if filters.get('practice_hours_min'):
            query = query.where(cls.practice_hours >= filters['practice_hours_min'])
        if filters.get('practice_hours_max'):
            query = query.where(cls.practice_hours <= filters['practice_hours_max'])
        if 'is_active' in filters and filters['is_active'] is not None:
            query = query.where(cls.is_active == filters['is_active'])

        total = query.count()

        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)

        items = []
        for record in query:
            items.append({
                'id': record.id,
                'discipline_id': record.discipline.id,
                'discipline_name': record.discipline.name,
                'group_id': record.group.id,
                'group_name': record.group.name,
                'semester_number': record.semester_number,
                'theory_hours': record.theory_hours,
                'practice_hours': record.practice_hours,
                'assessment_form': record.assessment_form,
                'is_active': record.is_active
            })

        return {
            'items': items,
            'total': total,
            'page': page,
            'page_size': page_size,
            'total_pages': (total + page_size - 1) // page_size if total > 0 else 0
        }

    def save(self, *args, **kwargs):
        self.updated_at = datetime.now()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.group.name} - {self.discipline.name} ({self.semester_number} семестр)"


def create_tables():
    """Создаёт все таблицы в базе данных"""
    db.connect()
    db.create_tables([Group, Discipline, Semester, Curriculum], safe=True)
    db.close()


def add_default_data():
    if Semester.select().count() == 0:
        for year in range(2024, 2027):
            for sem in range(1, 9):
                Semester.create(semester_number=sem, academic_year=f"{year}-{year+1}")
        print("Семестры добавлены")


if __name__ == "__main__":
    create_tables()
    add_default_data()
    print("База данных и таблицы созданы успешно!")
