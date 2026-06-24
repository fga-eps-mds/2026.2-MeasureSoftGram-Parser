import inspect
from genericparser.plugins.domain.generic_class import GenericStaticABC


def test_extract_abstract_method_uses_var_keyword_args():
    """
    Garante que o ABC declara a variael kwargs do extract VAR_KEYWORD.
    """
    sig = inspect.signature(GenericStaticABC.extract)
    params = list(sig.parameters.values())

    # Remove 'self'
    non_self_params = [p for p in params if p.name != "self"]

    assert len(non_self_params) == 1
    assert non_self_params[0].kind == inspect.Parameter.VAR_KEYWORD
