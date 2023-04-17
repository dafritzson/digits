from flask_wtf import FlaskForm
from wtforms import IntegerField, SelectField, SubmitField
from wtforms.validators import InputRequired, NumberRange


class DigitsForm(FlaskForm):
    difficulty = SelectField(
        "Difficulty:",
        choices=[("easy", "Easy"), ("medium", "Medium"), ("hard", "Hard")],
    )
    num_digits = IntegerField(
        "Number of Digits:",
        validators=[InputRequired(), NumberRange(min=3, max=6)],
        render_kw={
            "placeholder": 5,
        },
    )


def GuessForm(*args, **kwargs):
    class StaticForm(FlaskForm):
        submit_guess = SubmitField("Guess")
        submit_back = SubmitField("Play Again")
        num_digits = args[0]

    for i in range(args[0]):
        field = IntegerField(
            f"Digit {i+1}",
            validators=[InputRequired(), NumberRange(min=0, max=9)],
            render_kw={
                "placeholder": 0,
            },
        )
        setattr(StaticForm, f"digit_{i+1}", field)

    return StaticForm()
