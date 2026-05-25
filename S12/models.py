"""
Curriculum Plan Service (Сервис учебного плана) - Вариант №12
Модели базы данных для управления учебным планом
"""

from peewee import *

db = SqliteDatabase('S7.db')

class BaseModel(Model):
    """Базовая модель для всех таблиц"""
    class Meta:
        database = db

class Specialization(BaseModel):
    """Направление подготовки (шифр + название)"""
    code = CharField(primary_key=True, max_length=20, verbose_name="Шифр")
    name = CharField(max_length=255, verbose_name="Название")
    duration_training = IntegerField(verbose_name="Срок обучения (лет)")
    is_active = BooleanField(default=True, verbose_name="Активна")

    def __str__(self):
        return f"{self.code} - {self.name}"

    class Meta:
        table_name = 'specializations'

class Group(BaseModel):
    """Учебная группа"""
    number = IntegerField(verbose_name="Номер группы")
    prefix = CharField(max_length=10, verbose_name="Префикс")
    year_create = IntegerField(verbose_name="Год создания")
    status = CharField(max_length=20, default='active', verbose_name="Статус")
    
    specialization = ForeignKeyField(Specialization, backref='groups', 
                                     column_name='specialization_code', 
                                     verbose_name="Специализация")
    
    @property
    def full_name(self):
        """Полное наименование группы (пример: 3-2П9)"""
        return f"{self.number}-{self.prefix}"
    
    def __str__(self):
        return f"{self.full_name} ({self.year_create})"

    class Meta:
        table_name = 'groups'
        indexes = (
            (('number', 'prefix', 'year_create'), True),  
        )

class Discipline(BaseModel):
    """Дисциплина (учебный предмет)"""
    name = CharField(max_length=255, unique=True, verbose_name="Название")
    is_active = BooleanField(default=True, verbose_name="Активна")
    
    def __str__(self):
        return self.name

    class Meta:
        table_name = 'disciplines'

class Semester(BaseModel):
    """Семестр (номер + учебный год)"""
    semester_number = IntegerField(verbose_name="Номер семестра")
    academic_year = CharField(max_length=9, verbose_name="Учебный год")
    
    def __str__(self):
        return f"{self.semester_number} семестр ({self.academic_year})"

    class Meta:
        table_name = 'semesters'
        indexes = (
            (('semester_number', 'academic_year'), True),
        )

class Curriculum(BaseModel):
    """Учебный план (связь группы, дисциплины и семестра с часами)"""
    group = ForeignKeyField(Group, backref='curriculum_records', 
                           verbose_name="Группа")
    discipline = ForeignKeyField(Discipline, backref='curriculum_records', 
                                verbose_name="Дисциплина")
    semester_number = IntegerField(verbose_name="Номер семестра")

    theory_hours = IntegerField(default=0, verbose_name="Часы теории")
    practice_hours = IntegerField(default=0, verbose_name="Часы практики")
    assessment_form = CharField(max_length=10, 
                                choices=['exam', 'credit'], 
                                default='credit', 
                                verbose_name="Форма отчетности")

    is_active = BooleanField(default=True, verbose_name="Активна")
    
    @property
    def total_hours(self):
        """Общее количество часов (теория + практика) - вычисляемое поле"""
        return self.theory_hours + self.practice_hours
    
    def __str__(self):
        return f"{self.group.full_name} - {self.discipline.name} ({self.semester_number} семестр)"

    class Meta:
        table_name = 'curriculum'
        indexes = (
            (('group', 'discipline', 'semester_number'), True), 
            (('is_active',), False), 
        )

def init_db():
    """
    Инициализация базы данных.
    Создаёт все таблицы, если они не существуют.
    Все внешние ключи имеют ограничение NOT NULL (по умолчанию в Peewee).
    """
    db.create_tables([Specialization, Group, Discipline, Semester, Curriculum])
    
    if Specialization.select().count() == 0:
        Specialization.create(
            code='09.02.07',
            name='Информационные системы и программирование',
            duration_training=4
        )
        Specialization.create(
            code='09.02.01',
            name='Компьютерные системы и комплексы',
            duration_training=4
        )
        print("Специализации добавлены")
    
    if Semester.select().count() == 0:
        for year in range(2024, 2027):
            for sem in range(1, 9):
                Semester.create(
                    semester_number=sem,
                    academic_year=f"{year}-{year+1}"
                )
        print("Семестры добавлены")
    
    print("База данных успешно инициализирована!")

if __name__ == '__main__':
    db.connect()
    
    init_db()
    
    print("\n=== Созданные таблицы ===")
    tables = db.get_tables()
    for table in tables:
        print(f"  - {table}")
    
    db.close()
    print("\nБаза данных S7.db готова к работе!")
