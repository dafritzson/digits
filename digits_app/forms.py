from flask_wtf import FlaskForm
from wtforms import IntegerField, SelectField, SubmitField
from wtforms.validators import InputRequired, NumberRange


class DigitsForm(FlaskForm):
    difficulty = SelectField(
        "Difficulty:",
        choices=[("easy", "Easy"), ("medium", "Medium"), ("hard", "Hard")],
        default="medium",
    )
    num_digits = IntegerField(
        "Number of Digits:",
        default=5,
        validators=[InputRequired(), NumberRange(min=3, max=6)],
    )


class GuessButtons(FlaskForm):
    submit_play_again = SubmitField("Play Again")
    submit_reveal = SubmitField("Reveal")


def GuessForm(*args, **kwargs):
    class StaticForm(FlaskForm):
        submit_guess = SubmitField("Guess")
        num_digits = args[0]

    for i in range(args[0]):
        field = IntegerField(
            f"Digit {i+1}", validators=[InputRequired(), NumberRange(min=0, max=9)]
        )
        setattr(StaticForm, f"digit_{i+1}", field)

    return StaticForm()
