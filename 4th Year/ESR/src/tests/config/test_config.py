import json
import os
from pathlib import Path

import pytest

from config import load_node_config


def write_config(tmp_path: Path, name: str, data: dict):
    """
    Helper: cria a pasta network/ e escreve um ficheiro JSON lá dentro.
    """
    network_dir = tmp_path / "network"
    network_dir.mkdir(exist_ok=True)
    (network_dir / f"{name}.json").write_text(
        json.dumps(data, indent=2), encoding="utf-8"
    )


def test_load_node_config_server_netflix(tmp_path, monkeypatch):
    data = {
        "id": "Netflix",
        "role": "server",
        "neighbors": ["10.0.2.1"],
        "streams": ["movie.Mjpeg", "videobala.mp4"],
    }

    write_config(tmp_path, "Netflix", data)
    # correr o código como se o CWD fosse tmp_path
    monkeypatch.chdir(tmp_path)

    cfg = load_node_config("Netflix")

    assert cfg["id"] == "Netflix"
    assert cfg["role"] == "server"
    assert cfg["neighbors"] == ["10.0.2.1"]
    assert cfg["streams"] == ["movie.Mjpeg", "videobala.mp4"]


def test_load_node_config_transport_palma(tmp_path, monkeypatch):
    data = {
        "id": "Palma",
        "role": "transport",
        "neighbors": ["10.0.23.2", "10.0.18.1"],
        "streams": [],
    }

    write_config(tmp_path, "Palma", data)
    monkeypatch.chdir(tmp_path)

    cfg = load_node_config("Palma")

    assert cfg["id"] == "Palma"
    assert cfg["role"] == "transport"
    assert cfg["neighbors"] == ["10.0.23.2", "10.0.18.1"]
    assert cfg["streams"] == []


def test_load_node_config_client_fernando(tmp_path, monkeypatch):
    data = {
        "id": "Fernando",
        "role": "client",
        "neighbors": ["10.0.17.1"],
        "streams": [],
    }

    write_config(tmp_path, "Fernando", data)
    monkeypatch.chdir(tmp_path)

    cfg = load_node_config("Fernando")

    assert cfg["id"] == "Fernando"
    assert cfg["role"] == "client"
    assert cfg["neighbors"] == ["10.0.17.1"]
    assert cfg["streams"] == []


def test_load_node_config_missing_file(tmp_path, monkeypatch):
    """
    Se o ficheiro não existir, deve lançar FileNotFoundError.
    """
    # garantir que existe uma pasta network vazia
    (tmp_path / "network").mkdir(exist_ok=True)
    monkeypatch.chdir(tmp_path)

    with pytest.raises(FileNotFoundError):
        load_node_config("NaoExiste")
