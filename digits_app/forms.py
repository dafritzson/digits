from flask_wtf import FlaskForm
from wtforms import BooleanField, Field, IntegerField, SelectField, SubmitField
from wtforms.validators import InputRequired, NumberRange


class BooleanButtonField(Field):
    widget = None

    def __init__(self, label="", default_value: int = 0, validators=None, **kwargs):
        self.class_ = kwargs.pop("class_")
        self.default_value = default_value
        super().__init__(label, validators, **kwargs)
        self.html_params = {"name": self.name, "class": self.class_}

    def _value(self):
        return self.data or ""

    def process_formdata(self, valuelist):
        self.data = int(valuelist[0])

    def __call__(self, **kwargs):
        button_name = f"{self.name}"
        kwargs.setdefault("type", "button")
        kwargs.setdefault("id", button_name)
        kwargs.setdefault("value", self.default_value)
        html_params = self.html_params.copy()
        html_params.update(kwargs)
        html_params_str = " ".join(
            f'{key}="{value}"' for key, value in html_params.items()
        )
        hidden_input = (
            f'<input type="hidden" name="{button_name}" value={self.default_value}>'
        )
        return f"{hidden_input}<button {html_params_str}>{button_name}</button>"


class DigitsForm(FlaskForm):
    play_btn = SubmitField("Play")
    easy_btn = BooleanButtonField(
        "easy_btn", name="Easy", class_="boolean-button difficulty"
    )
    medium_btn = BooleanButtonField(
        "medium_btn",
        name="Medium",
        class_="boolean-button difficulty clicked",
        default_value=1,
    )
    hard_btn = BooleanButtonField(
        "hard_btn", name="Hard", class_="boolean-button difficulty"
    )

    three_btn = BooleanButtonField(
        "three_btn", name="3", class_="boolean-button num-digits"
    )
    four_btn = BooleanButtonField(
        "four_btn", name="4", class_="boolean-button num-digits"
    )
    five_btn = BooleanButtonField(
        "five_btn",
        name="5",
        class_="boolean-button num-digits clicked",
        default_value=1,
    )
    six_btn = BooleanButtonField(
        "six_btn", name="6", class_="boolean-button num-digits"
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
