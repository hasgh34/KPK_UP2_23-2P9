from peewee import *
from datetime import datetime

db = SqliteDatabase('curriculum.db')

class BaseModel(Model):
    class Meta:
        database = db

class Group(BaseModel):
    id = AutoField()
    name = CharField(max_length=100, unique=True, null=False)
    created_at = DateTimeField(default=datetime.now, null=False)

class Discipline(BaseModel):
    id = AutoField()
    name = CharField(max_length=200, unique=True, null=False)
    created_at = DateTimeField(default=datetime.now, null=False)

class Curriculum(BaseModel):
    id = AutoField()

    group = ForeignKeyField(Group, backref='curriculums', on_delete='CASCADE', null=False)
    discipline = ForeignKeyField(Discipline, backref='curriculums', on_delete='CASCADE', null=False)

    semester_number = IntegerField(
        null=False, 
        constraints=[Check('semester_number BETWEEN 1 AND 8')]
    )
    
    theory_hours = IntegerField(null=False, default=0, constraints=[Check('theory_hours >= 0')])
    practice_hours = IntegerField(null=False, default=0, constraints=[Check('practice_hours >= 0')])

    assessment_form = CharField(max_length=10, null=False, default='exam')

    is_active = BooleanField(default=True, null=False)
    
    created_at = DateTimeField(default=datetime.now, null=False)
    updated_at = DateTimeField(default=datetime.now, null=False)
    
    class Meta:
        constraints = [SQL('UNIQUE(group_id, discipline_id, semester_number)')]
    
    def save(self, *args, **kwargs):
        self.updated_at = datetime.now()
        return super().save(*args, **kwargs)
    
    @property
    def total_hours(self):
        """Вычисляемое поле total_hours"""
        return self.theory_hours + self.practice_hours

def create_tables():
    db.connect()
    db.create_tables([Group, Discipline, Curriculum], safe=True)
    db.close()

if __name__ == "__main__":
    create_tables()
    print(" База данных и таблицы созданы успешно!")
