import os
import sys

path = os.path.dirname(os.path.dirname(__file__))
sys.path.append(path)

from flask import Blueprint, Flask, redirect, render_template, request, session, url_for
from gevent.pywsgi import WSGIServer
from wtforms import IntegerField

from digits_app.forms import DigitsForm, GuessButtons, GuessForm
from digits_app.src.clues.clue_generator import ClueGenerator
from digits_app.src.constants import POS_RESPONSES
from digits_app.src.main import Digits
from digits_app.src.solver import Solver

app = Flask(__name__)
app.config["SECRET_KEY"] = "my-secret-key"
digits_bp = Blueprint("digits_bp", __name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

digits_obj = Digits()


@digits_bp.route("/", methods=["GET", "POST"])
def digits():
    form = DigitsForm()
    if not form.validate_on_submit():
        return render_template(
            "digits.html",
            form=form,
        )
    if form.easy_btn.data:
        session["difficulty"] = "easy"
    elif form.medium_btn.data:
        session["difficulty"] = "medium"
    elif form.hard_btn.data:
        session["difficulty"] = "hard"

    if form.three_btn.data:
        session["num_digits"] = int(form.three_btn.name)
    elif form.four_btn.data:
        session["num_digits"] = int(form.four_btn.name)
    elif form.five_btn.data:
        session["num_digits"] = int(form.five_btn.name)
    elif form.six_btn.data:
        session["num_digits"] = int(form.six_btn.name)
    solver_attempts = 3

    # Try to generate a solvable number up to 3 times before erroring.
    for _ in range(solver_attempts):
        session["answer"] = digits_obj.generate_answer(session["num_digits"])
        clue_gen = ClueGenerator(session["answer"], session["difficulty"])
        solver = Solver(
            clue_gen.digits,
            clue_gen.num_maps,
            clue_gen.clues,
            session["difficulty"],
            digits_obj.map_files,
        )
        if solver.final_clues is not None:
            clue_dict = {
                clue_type: [str(clue) for clue in _clues]
                for clue_type, _clues in solver.final_clues.items()
            }
            session["clues"] = clue_dict
            break
    if session.get("clues"):
        return redirect(url_for("digits_bp.guess"))
    return render_template(
        "digits.html",
        form=form,
    )


@digits_bp.route("/guess", methods=["GET", "POST"])
def guess():
    num_digits = session.get("num_digits")
    clues = session.get("clues")
    answer = session.get("answer")
    guess_form = GuessForm(num_digits, request.form)
    guess_buttons = GuessButtons()
    highlighted_clues = []
    guess_submitted = False

    guess = None
    number = answer
    guess_digits = [
        str(getattr(guess_form, f"digit_{digit}").data or 0)
        for digit in range(1, num_digits + 1)
    ]
    guess = int("".join(guess_digits))

    if "submit_reveal" in request.form:
        for i in range(num_digits):
            digit_field: IntegerField = getattr(guess_form, f"digit_{i+1}")
            digit_field.process_data(int(str(answer)[i]))

    if "submit_hint" in request.form and guess != answer:
        guess_clue_gen = ClueGenerator(guess, session.get("difficulty"))
        guess_clues = {
            Solver.format_clue_type(clue_key): list(map(str, clues))
            for clue_key, clues in guess_clue_gen.clues.items()
        }
        for clue_type, _clues in clues.items():
            if len(guess_clues[clue_type]) > len(_clues):
                highlighted_clues.append(_clues[-1])
            unsatisfied_clues = list(
                set(_clues).difference(set(guess_clues[clue_type]))
            )
            highlighted_clues.extend(unsatisfied_clues)
    if "submit_play_again" in request.form:
        return redirect(url_for("digits_bp.digits"))
    if "submit_guess" in request.form:
        guess_submitted = True
    return render_template(
        "guess.html",
        form=guess_form,
        clues=clues,
        highlighted_clues=highlighted_clues,
        guess=guess,
        guess_submitted=guess_submitted,
        number=number,
        buttons=guess_buttons,
        congratulations_messages=POS_RESPONSES,
    )


app.register_blueprint(digits_bp)

if __name__ == "__main__":
    # http_server = WSGIServer(('', 5000), app)
    # http_server.serve_forever()
    app.run(debug=True, host="0.0.0.0")
