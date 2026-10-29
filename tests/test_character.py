import pytest

# Ces tests demandent Manim : ils sont ignorés si les outils vidéo ne sont pas installés.
pytest.importorskip("manim")

from rago.character import EXPRESSIONS, Rago  # noqa: E402


@pytest.mark.parametrize("expression", list(EXPRESSIONS))
def test_rago_builds_with_every_expression(expression):
    rago = Rago(expression)
    assert rago.expression == expression
    assert len(rago.face) > 0


def test_unknown_expression_is_rejected():
    with pytest.raises(ValueError, match="Expression inconnue"):
        Rago("furieux")


def test_set_expression_keeps_size_and_position():
    rago = Rago().scale(0.5).shift([2, 1, 0])
    height, center = rago.height, rago.screen.get_center()
    rago.set_expression("perdu")
    assert rago.expression == "perdu"
    assert rago.screen.get_center() == pytest.approx(center)
    assert rago.height == pytest.approx(height, rel=0.05)


def test_set_expression_moves_face_with_rago():
    rago = Rago().scale(0.5).shift([2, 1, 0])
    rago.set_expression("content")
    assert rago.face.get_center()[0] == pytest.approx(rago.screen.get_center()[0], abs=0.1)
