from peewee import *
from datetime import datetime

db = SqliteDatabase('curriculum.db')


class BaseModel(Model):
    class Meta:
        database = db


class AssessmentForm:
    EXAM = 'exam'
    CREDIT = 'credit'
    CHOICES = [EXAM, CREDIT]


class Group(BaseModel):
    id = AutoField(primary_key=True)
    name = CharField(max_length=100, unique=True, null=False)
    created_at = DateTimeField(default=datetime.now, null=False)

    class Meta:
        table_name = 'groups'


class Discipline(BaseModel):
    id = AutoField(primary_key=True)
    name = CharField(max_length=200, unique=True, null=False)
    created_at = DateTimeField(default=datetime.now, null=False)

    class Meta:
        table_name = 'disciplines'


class Semester(BaseModel):
    id = AutoField(primary_key=True)
    semester_number = IntegerField(null=False, constraints=[Check('semester_number BETWEEN 1 AND 8')])
    academic_year = CharField(max_length=9, null=False)

    class Meta:
        table_name = 'semesters'
        constraints = [SQL('UNIQUE(semester_number, academic_year)')]

    def __str__(self):
        return f"{self.semester_number} семестр ({self.academic_year})"


class Curriculum(BaseModel):
    id = AutoField(primary_key=True)


    group = ForeignKeyField(Group, backref='curriculums', on_delete='CASCADE', null=False)
    discipline = ForeignKeyField(Discipline, backref='curriculums', on_delete='CASCADE', null=False)
    semester = ForeignKeyField(Semester, backref='curriculums', on_delete='RESTRICT', null=False)


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
        choices=AssessmentForm.CHOICES,
        constraints=[Check("assessment_form IN ('exam', 'credit')")]
    )

    is_active = BooleanField(default=True, null=False)


    created_at = DateTimeField(default=datetime.now, null=False)
    updated_at = DateTimeField(default=datetime.now, null=False)

    class Meta:
        table_name = 'curriculum'
        constraints = [
            SQL('UNIQUE(group_id, discipline_id, semester_id)')  
        ]
        order_by = ['-is_active', 'id']



    @classmethod
    def _validate_hours(cls, theory_hours, practice_hours):
        if theory_hours is not None and theory_hours < 0:
            raise ValueError(f"theory_hours должно быть >= 0, получено {theory_hours}")
        if practice_hours is not None and practice_hours < 0:
            raise ValueError(f"practice_hours должно быть >= 0, получено {practice_hours}")

    @classmethod
    def _validate_assessment_form(cls, assessment_form):
        if assessment_form is not None and assessment_form not in AssessmentForm.CHOICES:
            raise ValueError(f"assessment_form должно быть 'exam' или 'credit', получено {assessment_form}")



    @classmethod
    def create(cls, **kwargs):


        required_fields = ['group', 'discipline', 'semester', 'theory_hours', 'practice_hours', 'assessment_form']
        for field in required_fields:
            if field not in kwargs:
                raise ValueError(f"Поле '{field}' обязательно для создания")


        cls._validate_hours(kwargs.get('theory_hours'), kwargs.get('practice_hours'))

        cls._validate_assessment_form(kwargs.get('assessment_form'))

        return super().create(**kwargs)

    def save(self, *args, **kwargs):

        self._validate_hours(self.theory_hours, self.practice_hours)

        self._validate_assessment_form(self.assessment_form)

        self.updated_at = datetime.now()
        return super().save(*args, **kwargs)

    @classmethod
    def get_by_id_with_names(cls, record_id):

        try:
            record = cls.get_by_id(record_id)


            discipline_name = record.discipline.name if record.discipline else None
            group_name = record.group.name if record.group else None
            semester_number = record.semester.semester_number if record.semester else None

            return {
                'id': record.id,
                'discipline_id': record.discipline.id if record.discipline else None,
                'discipline_name': discipline_name,
                'group_id': record.group.id if record.group else None,
                'group_name': group_name,
                'semester_number': semester_number,
                'theory_hours': record.theory_hours,
                'practice_hours': record.practice_hours,
                'assessment_form': record.assessment_form,
                'is_active': record.is_active
            }
        except DoesNotExist:
            return None

    def soft_delete(self):

        try:

            if self.id is None:
                return False

            if self.is_active:
                self.is_active = False
                self.save()
                return True
            return False
        except DoesNotExist:
            return False

    def update_fields(self, **kwargs):
        forbidden_fields = ['group', 'group_id', 'discipline', 'discipline_id', 'semester', 'semester_id']

        for field in forbidden_fields:
            if field in kwargs:
                raise ValueError(f"Поле '{field}' нельзя изменить после создания")


        if 'theory_hours' in kwargs or 'practice_hours' in kwargs:
            self._validate_hours(
                kwargs.get('theory_hours', self.theory_hours),
                kwargs.get('practice_hours', self.practice_hours)
            )
        if 'assessment_form' in kwargs:
            self._validate_assessment_form(kwargs['assessment_form'])


        allowed_fields = ['theory_hours', 'practice_hours', 'assessment_form']

        for key, value in kwargs.items():
            if key in allowed_fields:
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
            query = query.where(cls.group_id == filters['group_id'])
        if filters.get('discipline_id'):
            query = query.where(cls.discipline_id == filters['discipline_id'])
        if filters.get('semester_number'):

            semester_ids = Semester.select(Semester.id).where(Semester.semester_number == filters['semester_number'])
            query = query.where(cls.semester_id.in_(semester_ids))
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

        query = query.order_by(cls.id)

        total = query.count()

        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)

        items = []
        for record in query:
            items.append({
                'id': record.id,
                'discipline_id': record.discipline_id,
                'discipline_name': record.discipline.name if record.discipline else None,
                'group_id': record.group_id,
                'group_name': record.group.name if record.group else None,
                'semester_number': record.semester.semester_number if record.semester else None,
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

    def __str__(self):
        semester_str = str(self.semester) if self.semester else "неизвестный семестр"
        return f"{self.group.name} - {self.discipline.name} ({semester_str})"


def create_tables():
    db.connect()
    db.create_tables([Group, Discipline, Semester, Curriculum], safe=True)
    db.close()


def add_default_data():
    if Semester.select().count() == 0:
        for year in range(2024, 2027):
            for sem in range(1, 9):
                Semester.create(semester_number=sem, academic_year=f"{year}-{year+1}")
        print("✓ Семестры добавлены")

    if Group.select().count() == 0:
        Group.create(name="3-2П9")
        Group.create(name="4-2П9")
        print("✓ Тестовые группы добавлены")

    if Discipline.select().count() == 0:
        Discipline.create(name="Базы данных")
        Discipline.create(name="Программирование")
        print("Тестовые дисциплины добавлены")


if __name__ == "__main__":
    create_tables()
    add_default_data()
    print("База данных и таблицы созданы успешно!")
