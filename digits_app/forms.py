from flask_wtf import FlaskForm
from wtforms import BooleanField, Field, IntegerField, SelectField, SubmitField
from wtforms.validators import InputRequired, NumberRange


class BooleanButtonField(Field):
    widget = None

    def __init__(self, label="", validators=None, **kwargs):
        super().__init__(label, validators, **kwargs)
        self.html_params = {"name": self.name}

    def _value(self):
        return self.data or ""

    def process_formdata(self, valuelist):
        print(f"Processing form data for {self.name}: {valuelist}")
        if valuelist[0] == "1":
            self.data = True
        else:
            self.data = False

    def __call__(self, **kwargs):
        button_name = f"{self.name}"
        kwargs.setdefault("type", "button")
        kwargs.setdefault("class", "boolean-button")
        kwargs.setdefault("onclick", f"setButtonValue({button_name})")
        kwargs.setdefault("id", button_name)
        html_params = self.html_params.copy()
        html_params.update(kwargs)
        html_params_str = " ".join(
            f'{key}="{value}"' for key, value in html_params.items()
        )
        hidden_input = f'<input type="hidden" name="{button_name}" value=0>'
        return f"{hidden_input}<button {html_params_str}>{button_name}</button>"


class DigitsForm(FlaskForm):
    num_digits = IntegerField(
        "Number of Digits:",
        default=5,
        validators=[InputRequired(), NumberRange(min=3, max=6)],
    )
    play_btn = SubmitField("Play")
    easy_btn = BooleanButtonField("Easy", name="Easy")
    medium_btn = BooleanButtonField("Medium", name="Medium")
    hard_btn = BooleanButtonField("Hard", name="Hard")


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
