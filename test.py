"""Тесты"""
import unittest
from unittest.mock import patch, MagicMock
import json
import yaml
import os
import tempfile

from decorator import (
    ConcreteComponent,
    YamlDecorator,
    CsvDecorator,
)


class TestCurrencyDecorator(unittest.TestCase):
    """Тесты базового компонента и декораторов (по 2 теста на каждый)."""

    # ====================== 2 теста для ConcreteComponent ======================
    @patch("decorator.urllib.request.urlopen")
    def test_concrete_component_operation(self, mock_urlopen):
        """Тест 1: проверка возврата JSON и структуры данных."""
        mock_response = MagicMock()
        mock_response.read.return_value = (
            b'{"Date":"14.04.2026","Valute":{"USD":{"CharCode":"USD","Value":100.0}}}'
        )
        mock_urlopen.return_value.__enter__.return_value = mock_response

        comp = ConcreteComponent()
        result = comp.operation()

        self.assertIsInstance(result, str)
        data = json.loads(result)
        self.assertIn("Valute", data)
        self.assertIn("USD", data["Valute"])

    @patch("decorator.urllib.request.urlopen")
    def test_concrete_component_pretty_json(self, mock_urlopen):
        """Тест 2: проверка, что JSON красиво отформатирован (indent)."""
        mock_response = MagicMock()
        mock_response.read.return_value = b'{"Date":"14.04.2026"}'
        mock_urlopen.return_value.__enter__.return_value = mock_response

        comp = ConcreteComponent()
        result = comp.operation()
        self.assertIn("\n  ", result)  # indent=2

    # ====================== 2 теста для YamlDecorator ======================
    @patch("decorator.urllib.request.urlopen")
    def test_yaml_decorator_operation(self, mock_urlopen):
        """Тест 1: проверка преобразования в YAML."""
        mock_response = MagicMock()
        mock_response.read.return_value = (
            b'{"Date":"14.04.2026","Valute":{"USD":{"CharCode":"USD"}}}'
        )
        mock_urlopen.return_value.__enter__.return_value = mock_response

        base = ConcreteComponent()
        dec = YamlDecorator(base)
        result = dec.operation()

        self.assertIsInstance(result, str)
        data = yaml.safe_load(result)
        self.assertEqual(data["Date"], "14.04.2026")

    @patch("decorator.urllib.request.urlopen")
    def test_yaml_decorator_save(self, mock_urlopen):
        """Тест 2: проверка сохранения в YAML-файл."""
        mock_response = MagicMock()
        mock_response.read.return_value = b'{"Date":"14.04.2026"}'
        mock_urlopen.return_value.__enter__.return_value = mock_response

        base = ConcreteComponent()
        dec = YamlDecorator(base)

        with tempfile.TemporaryDirectory() as tmp:
            fname = os.path.join(tmp, "test.yaml")
            dec.save_to_file(fname)
            self.assertTrue(os.path.exists(fname))

            with open(fname, encoding="utf-8") as f:
                content = f.read()
            self.assertIn("Date:", content)

    # ====================== 2 теста для CsvDecorator ======================
    @patch("decorator.urllib.request.urlopen")
    def test_csv_decorator_operation(self, mock_urlopen):
        """Тест 1: проверка преобразования в CSV."""
        mock_response = MagicMock()
        mock_response.read.return_value = (
            b'{"Date":"14.04.2026","Valute":{"USD":{"CharCode":"USD","Value":100}}}'
        )
        mock_urlopen.return_value.__enter__.return_value = mock_response

        base = ConcreteComponent()
        dec = CsvDecorator(base)
        result = dec.operation()

        self.assertIsInstance(result, str)
        self.assertIn("Дата:", result)
        self.assertIn("USD", result)

    @patch("decorator.urllib.request.urlopen")
    def test_csv_decorator_save(self, mock_urlopen):
        """Тест 2: проверка сохранения в CSV-файл."""
        mock_response = MagicMock()
        mock_response.read.return_value = b'{"Date":"14.04.2026"}'
        mock_urlopen.return_value.__enter__.return_value = mock_response

        base = ConcreteComponent()
        dec = CsvDecorator(base)

        with tempfile.TemporaryDirectory() as tmp:
            fname = os.path.join(tmp, "test.csv")
            dec.save_to_file(fname)
            self.assertTrue(os.path.exists(fname))

            with open(fname, encoding="utf-8") as f:
                content = f.read()
            self.assertIn("Дата:", content)


if __name__ == "__main__":
    unittest.main(verbosity=2)