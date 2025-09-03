from __future__ import annotations

import argparse
import json
from pathlib import Path
from .report_generator import generate_dashboard_html, load_json, save_dashboard


def main() -> None:
    parser = argparse.ArgumentParser(description="Genera reporte HTML")
    parser.add_argument("input", help="Archivo JSON con datos del reporte")
    parser.add_argument("--output", default="reporte.html", help="Archivo de salida")
    args = parser.parse_args()

    path = Path(args.input)
    data = load_json(path)
    save_dashboard(data, Path(args.output))

if __name__ == "__main__":
    main()

