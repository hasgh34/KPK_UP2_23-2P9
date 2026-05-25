from peewee import *
from datetime import datetime

db = SqliteDatabase('curriculum_plan.db')

class BaseModel(Model):
    class Meta:
        database = db

class Group(BaseModel):
    id = AutoField()
    name = CharField(max_length=100, unique=True, verbose_name="Название группы")
    created_at = DateTimeField(default=datetime.now)

class Discipline(BaseModel):
    id = AutoField()
    name = CharField(max_length=200, unique=True, verbose_name="Название дисциплины")
    created_at = DateTimeField(default=datetime.now)

class Curriculum(BaseModel):
    id = AutoField()
    
    group = ForeignKeyField(Group, backref='curriculums', on_delete='CASCADE', null=False)
    discipline = ForeignKeyField(Discipline, backref='curriculums', on_delete='CASCADE', null=False)
    
    semester_number = IntegerField(null=False, constraints=[Check('semester_number >= 1')])
    
    lecture_hours = IntegerField(null=False, default=0, constraints=[Check('lecture_hours >= 0')])
    practice_hours = IntegerField(null=False, default=0, constraints=[Check('practice_hours >= 0')])
    total_hours = IntegerField(null=False, constraints=[Check('total_hours >= 0')])
    
    exam_form = BooleanField(default=False, verbose_name="Экзамен")
    credit_form = BooleanField(default=False, verbose_name="Зачёт")
    
    is_active = BooleanField(default=True, null=False)
    
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)
    
    def save(self, *args, **kwargs):
        self.updated_at = datetime.now()
        return super().save(*args, **kwargs)

def create_tables():
    db.connect()
    db.create_tables([Group, Discipline, Curriculum], safe=True)
    db.close()
