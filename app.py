from flask import Blueprint, Flask, redirect, render_template, request, url_for
from gevent.pywsgi import WSGIServer

from forms import DigitsForm, GuessForm
from src.clues.clue_generator import ClueGenerator
from src.main import Digits
from src.solver import Solver

app = Flask(__name__)
app.config["SECRET_KEY"] = "my-secret-key"
digits_bp = Blueprint("digits_bp", __name__, url_prefix="/digits")


digits_obj = Digits()


@digits_bp.route("/", methods=["GET", "POST"])
def digits():
    form = DigitsForm()
    if form.validate_on_submit():
        digits_obj.difficulty = form.difficulty.data
        digits_obj.num_digits = form.num_digits.data
        digits_obj.answer = digits_obj.generate_answer(digits_obj.num_digits)
        return redirect(url_for("digits_bp.guess"))
    return render_template("digits.html", form=form)


@digits_bp.route("/guess", methods=["GET", "POST"])
def guess():
    guess_form = GuessForm(digits_obj.num_digits, request.form)
    clue_gen = ClueGenerator(digits_obj.answer, digits_obj.difficulty)
    solver = Solver(
        clue_gen.digits,
        clue_gen.num_maps,
        clue_gen.clues,
        digits_obj.difficulty,
        digits_obj.map_files,
    )
    digits_obj.clues = solver.final_clues
    str_clues = []
    for clues in digits_obj.clues.values():
        for clue in clues:
            str_clues.append(str(clue))

    guess = None
    number = digits_obj.answer
    if guess_form.validate_on_submit():
        if "submit_guess" in request.form:
            guess_digits = [
                str(getattr(guess_form, f"digit_{digit}").data)
                for digit in range(1, digits_obj.num_digits + 1)
            ]
            guess = int("".join(guess_digits))
        elif "submit_back" in request.form:
            return redirect(url_for("digits_bp.digits"))
    return render_template(
        "guess.html",
        form=guess_form,
        clues=str_clues,
        guess=guess,
        number=number,
        digits_obj=digits_obj,
    )


app.register_blueprint(digits_bp)

if __name__ == "__main__":
    http_server = WSGIServer(('', 5000), app)
    http_server.serve_forever()
