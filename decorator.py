"""Модуль реализует паттерн Decorator для форматирования курсов валют ЦБ РФ."""
from __future__ import annotations

import urllib.request
import json
import yaml
import csv
import io
from abc import ABC, abstractmethod
from typing import Any


class Component(ABC):
    """Базовый интерфейс Компонента определяет поведение,
    которое изменяется декораторами."""

    @abstractmethod
    def operation(self) -> str:
        """Возвращает курсы валют в заданном формате."""
        pass


class ConcreteComponent(Component):
    """Конкретный компонент, возвращающий данные в формате JSON
    с помощью API Центробанка РФ."""

    def operation(self) -> str:
        """Получает актуальные курсы валют и возвращает их в виде JSON-строки.

        Returns:
            str: JSON-строка с курсами валют.
        """
        url = "https://www.cbr-xml-daily.ru/daily_json.js"
        with urllib.request.urlopen(url) as response:
            data: dict[str, Any] = json.loads(response.read().decode("utf-8"))
        return json.dumps(data, ensure_ascii=False, indent=2)


class Decorator(Component):
    """Базовый класс Декоратора. Следует интерфейсу Component
    и делегирует работу обёрнутому компоненту."""

    def __init__(self, component: Component) -> None:
        self._component: Component = component

    def operation(self) -> str:
        """Делегирует вызов обёрнутому компоненту."""
        return self._component.operation()


class YamlDecorator(Decorator):
    """Декоратор, преобразующий результат базового компонента в YAML-формат."""

    def operation(self) -> str:
        """Преобразует JSON-результат в YAML-строку.

        Returns:
            str: Данные в формате YAML.
        """
        json_str = self._component.operation()
        data: dict[str, Any] = json.loads(json_str)
        return yaml.dump(
            data,
            allow_unicode=True,
            default_flow_style=False,
            sort_keys=False,
        )

    def save_to_file(self, filename: str = "rates.yaml") -> None:
        """Сохраняет данные в YAML-файл.

        Args:
            filename (str): Имя файла для сохранения.
        """
        with open(filename, "w", encoding="utf-8") as f:
            f.write(self.operation())


class CsvDecorator(Decorator):
    """Декоратор, преобразующий результат базового компонента в CSV-формат."""

    def operation(self) -> str:
        """Преобразует JSON-результат в CSV-строку.

        Returns:
            str: Данные в формате CSV (с шапкой и датой).
        """
        json_str = self._component.operation()
        data: dict[str, Any] = json.loads(json_str)

        output = io.StringIO(newline="")
        writer = csv.writer(output)

        # Добавляем дату
        writer.writerow(["Дата:", data.get("Date", "N/A")])
        writer.writerow([])

        # Шапка таблицы
        writer.writerow(["CharCode", "NumCode", "Nominal", "Name", "Value", "Previous"])

        for valute in data.get("Valute", {}).values():
            writer.writerow(
                [
                    valute.get("CharCode", ""),
                    valute.get("NumCode", ""),
                    valute.get("Nominal", ""),
                    valute.get("Name", ""),
                    valute.get("Value", ""),
                    valute.get("Previous", ""),
                ]
            )

        return output.getvalue()

    def save_to_file(self, filename: str = "rates.csv") -> None:
        """Сохраняет данные в CSV-файл.

        Args:
            filename (str): Имя файла для сохранения.
        """
        with open(filename, "w", encoding="utf-8", newline="") as f:
            f.write(self.operation())


if __name__ == "__main__":
    print("Клиент: Получаем базовый JSON")
    simple = ConcreteComponent()
    print("RESULT (JSON, первые 300 символов):")
    print(simple.operation()[:300] + "...\n")

    print("Клиент: YAML-декоратор")
    yaml_dec = YamlDecorator(simple)
    print("RESULT (YAML, первые 300 символов):")
    print(yaml_dec.operation()[:300] + "...")
    yaml_dec.save_to_file()
    print(f"✅ Сохранено в rates.yaml\n")

    print("Клиент: CSV-декоратор")
    csv_dec = CsvDecorator(simple)
    print("RESULT (CSV, первые 300 символов):")
    print(csv_dec.operation()[:300] + "...")
    csv_dec.save_to_file()
    print(f"✅ Сохранено в rates.csv")