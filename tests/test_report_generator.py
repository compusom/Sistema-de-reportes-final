from pathlib import Path
import json
from src.report_generator import generate_dashboard_html

def test_generate_dashboard_html(tmp_path):
    data = json.loads(Path('tests/data.json').read_text())
    html = generate_dashboard_html(data)
    assert '<h1>Reporte:' in html
    assert 'Embudo' in html
    assert 'Top Anuncios' in html
