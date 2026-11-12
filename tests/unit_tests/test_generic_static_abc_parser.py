import json

import pytest

from genericparser.plugins.domain.generic_class import GenericStaticABC


class ParserFake(GenericStaticABC):
    """Plugin mínimo: devolve o que recebeu no ``retorno``."""

    def __init__(self, retorno=None):
        self.retorno = retorno
        self.recebido = None

    def extract(self, **kwargs):
        self.recebido = kwargs
        return self.retorno


RETORNO_VALIDO = {"metrics": ["m"], "values": [1], "file_paths": ["a.py"]}


def test_extract_da_classe_base_levanta_not_implemented():
    plugin = ParserFake()

    with pytest.raises(NotImplementedError):
        GenericStaticABC.extract(plugin)


def test_parser_exige_input_value():
    plugin = ParserFake(RETORNO_VALIDO)

    with pytest.raises(Exception, match="kwargs must have input_value key"):
        plugin.parser(filters=None)


def test_parser_repassa_entrada_e_filtros_ao_extract():
    plugin = ParserFake(RETORNO_VALIDO)

    assert plugin.parser(input_value={"repository": "org/repo"}, filters={"dates": None}) == RETORNO_VALIDO
    assert plugin.recebido == {"input_file": {"repository": "org/repo"}, "filters": {"dates": None}}


def test_entrada_em_arquivo_json_achata_listas_e_objetos(tmp_path):
    arquivo = tmp_path / "entrada.json"
    arquivo.write_text(json.dumps({"componentes": [{"a": 1}, {"b": 2}], "base": {"c": 3}}))

    assert ParserFake().get_if_input_is_file_or_str(str(arquivo)) == [{"a": 1}, {"b": 2}, {"c": 3}]


def test_texto_que_nao_e_arquivo_volta_como_veio():
    assert ParserFake().get_if_input_is_file_or_str("org/repo") == "org/repo"


@pytest.mark.parametrize(
    "retorno, mensagem",
    [
        (["nao", "e", "dict"], "must be a list"),
        ({"metrics": [], "values": []}, "must have file_paths key"),
        ({"values": [], "file_paths": []}, "must have metrics key"),
        ({"metrics": [], "file_paths": []}, "must have values key"),
    ],
)
def test_retorno_invalido_do_plugin_levanta_erro(retorno, mensagem):
    plugin = ParserFake()

    with pytest.raises(Exception, match=mensagem):
        plugin.validate_return_type(retorno)
