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

    class Meta:
        table_name = 'groups'


class Discipline(BaseModel):
    id = AutoField(primary_key=True)
    name = CharField(max_length=200, unique=True, null=False)

    class Meta:
        table_name = 'disciplines'


class Curriculum(BaseModel):
    id = AutoField(primary_key=True)

    group_id = IntegerField(null=False)  
    discipline_id = IntegerField(null=False)  

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

    class Meta:
        table_name = 'curriculum'
        constraints = [
            SQL('UNIQUE(group_id, discipline_id, semester_number)')
        ]
        indexes = (
            (('group_id',), False),
            (('discipline_id',), False),
            (('semester_number',), False),
            (('is_active',), False),
        )


    @classmethod
    def _validate_required_fields(cls, **kwargs):
        required_fields = ['group_id', 'discipline_id', 'semester_number', 
                          'theory_hours', 'practice_hours', 'assessment_form']
        missing = [f for f in required_fields if f not in kwargs or kwargs[f] is None]
        if missing:
            raise ValueError(f"Отсутствуют обязательные поля: {', '.join(missing)}")

    @classmethod
    def _validate_hours(cls, theory_hours, practice_hours):
        if theory_hours < 0:
            raise ValueError(f"theory_hours должно быть >= 0, получено {theory_hours}")
        if practice_hours < 0:
            raise ValueError(f"practice_hours должно быть >= 0, получено {practice_hours}")

    @classmethod
    def _validate_semester(cls, semester_number):
        if not (1 <= semester_number <= 8):
            raise ValueError(f"semester_number должно быть от 1 до 8, получено {semester_number}")

    @classmethod
    def _validate_assessment_form(cls, assessment_form):
        if assessment_form not in AssessmentForm.CHOICES:
            raise ValueError(f"assessment_form должно быть 'exam' или 'credit', получено {assessment_form}")



    @classmethod
    def create_curriculum(cls, **kwargs):
        cls._validate_required_fields(**kwargs)

        cls._validate_semester(kwargs['semester_number'])
        cls._validate_hours(kwargs['theory_hours'], kwargs['practice_hours'])
        cls._validate_assessment_form(kwargs['assessment_form'])

        return cls.create(**kwargs)

    @classmethod
    def get_by_id_with_names(cls, record_id):
        try:
            record = cls.get_by_id(record_id)
            return {
                'id': record.id,
                'discipline_id': record.discipline_id,
                'discipline_name': f"Дисциплина_{record.discipline_id}",  
                'group_id': record.group_id,
                'group_name': f"Группа_{record.group_id}",  
                'semester_number': record.semester_number,
                'theory_hours': record.theory_hours,
                'practice_hours': record.practice_hours,
                'assessment_form': record.assessment_form,
                'is_active': record.is_active
            }
        except DoesNotExist:
            return None

    def soft_delete(self):
        if not self.is_active:
            return False
        self.is_active = False
        self.save()
        return True

    def update_fields(self, **kwargs):
        forbidden_fields = ['group_id', 'discipline_id', 'semester_number', 'id', 'is_active']

        for field in forbidden_fields:
            if field in kwargs:
                raise ValueError(f"Поле '{field}' нельзя изменить после создания")

        if 'theory_hours' in kwargs or 'practice_hours' in kwargs:
            theory = kwargs.get('theory_hours', self.theory_hours)
            practice = kwargs.get('practice_hours', self.practice_hours)
            self._validate_hours(theory, practice)

        if 'assessment_form' in kwargs:
            self._validate_assessment_form(kwargs['assessment_form'])

        allowed_fields = ['theory_hours', 'practice_hours', 'assessment_form']

        for key, value in kwargs.items():
            if key in allowed_fields:
                setattr(self, key, value)

        self.save()
        return self

    @classmethod
    def get_filtered_list(cls, filters=None, page=1, page_size=20):
        query = cls.select()

        if filters is None:
            filters = {}

        apply_default_active = 'is_active' not in filters or filters['is_active'] is None
        if apply_default_active:
            query = query.where(cls.is_active == True)

        if filters.get('group_id') is not None:
            query = query.where(cls.group_id == filters['group_id'])
        if filters.get('discipline_id') is not None:
            query = query.where(cls.discipline_id == filters['discipline_id'])
        if filters.get('semester_number') is not None:
            query = query.where(cls.semester_number == filters['semester_number'])
        if filters.get('assessment_form') is not None:
            query = query.where(cls.assessment_form == filters['assessment_form'])

        if filters.get('theory_hours_min') is not None:
            query = query.where(cls.theory_hours >= filters['theory_hours_min'])
        if filters.get('theory_hours_max') is not None:
            query = query.where(cls.theory_hours <= filters['theory_hours_max'])
        if filters.get('practice_hours_min') is not None:
            query = query.where(cls.practice_hours >= filters['practice_hours_min'])
        if filters.get('practice_hours_max') is not None:
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
                'discipline_name': f"Дисциплина_{record.discipline_id}",  # Заглушка
                'group_id': record.group_id,
                'group_name': f"Группа_{record.group_id}",  # Заглушка
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

    def __str__(self):
        return f"Group_{self.group_id} - Discipline_{self.discipline_id} ({self.semester_number} семестр)"


def create_tables():
    """Создаёт таблицы в базе данных"""
    db.connect()
    db.create_tables([Group, Discipline, Curriculum], safe=True)
    db.close()


if __name__ == "__main__":
    create_tables()
    print("База данных и таблицы созданы успешно!")
