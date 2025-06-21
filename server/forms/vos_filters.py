from flask_wtf import FlaskForm
from wtforms import SubmitField, SelectMultipleField, RadioField
from wtforms.validators import DataRequired
from wtforms.widgets import ListWidget, CheckboxInput


class FilterVosFinals(FlaskForm):
    statuses = SelectMultipleField('Статусы',
        widget=ListWidget(prefix_label=False),
        option_widget=CheckboxInput(),
        choices=[('Участник', 'Участник'),
                 ('Призер', 'Призер'),
                 ('Победитель', 'Победитель')
                 ]
    )
    numbers = SelectMultipleField('Классы',
        widget=ListWidget(prefix_label=False),
        option_widget=CheckboxInput(),
        choices=[(str(i), str(i) + ' класс') for i in range(6, 12)], coerce=int
    )
    subjects = SelectMultipleField('Предметы',
        widget=ListWidget(prefix_label=False),
        option_widget=CheckboxInput(),
        choices=[]
    )
    index = RadioField('Индекс (группировка)', choices=[
        ('fio', 'По участникам'),
        ('subject', 'По предметам')
    ], validators=[DataRequired()])
    submit = SubmitField('Применить')
