import sys
import types


def _install_stubs(monkeypatch):
    addict = types.ModuleType("addict")

    class Dict(dict):
        def __getattr__(self, key):
            return self.get(key)

    addict.Dict = Dict
    monkeypatch.setitem(sys.modules, "addict", addict)

    num2words = types.ModuleType("num2words")
    num2words.num2words = lambda *args, **kwargs: "stub"
    monkeypatch.setitem(sys.modules, "num2words", num2words)

    spacy = types.ModuleType("spacy")
    spacy.load = lambda *args, **kwargs: None
    monkeypatch.setitem(sys.modules, "spacy", spacy)

    regex = types.ModuleType("regex")
    regex.compile = lambda *args, **kwargs: None
    regex.match = lambda *args, **kwargs: None
    regex.findall = lambda *args, **kwargs: []
    regex.sub = lambda *args, **kwargs: ""
    monkeypatch.setitem(sys.modules, "regex", regex)

    transformers = types.ModuleType("transformers")
    transformers.BartForConditionalGeneration = object
    monkeypatch.setitem(sys.modules, "transformers", transformers)

    torch = types.ModuleType("torch")
    monkeypatch.setitem(sys.modules, "torch", torch)

    fugashi = types.ModuleType("fugashi")
    fugashi.Tagger = object
    monkeypatch.setitem(sys.modules, "fugashi", fugashi)

    jaconv = types.ModuleType("jaconv")
    jaconv.kata2hira = lambda text: text
    monkeypatch.setitem(sys.modules, "jaconv", jaconv)

    mojimoji = types.ModuleType("mojimoji")
    mojimoji.zen_to_han = lambda text, kana=False: text
    mojimoji.han_to_zen = lambda text, digit=False, ascii=False: text
    monkeypatch.setitem(sys.modules, "mojimoji", mojimoji)


def test_resource_loading_uses_files_api(monkeypatch):
    _install_stubs(monkeypatch)

    import importlib.resources

    def boom(*args, **kwargs):
        raise AssertionError("open_text should not be used")

    monkeypatch.setattr(importlib.resources, "open_text", boom, raising=False)

    import misaki.cutlet  # noqa: F401
    import misaki.en  # noqa: F401
