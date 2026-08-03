from pathlib import Path

import pandas as pd

from app.exports.common import lead_to_flat_dict
from app.models.lead import Lead


def export_csv(leads: list[Lead], out_path: Path) -> Path:
    rows = [lead_to_flat_dict(lead) for lead in leads]
    df = pd.DataFrame(rows)
    df.to_csv(out_path, index=False)
    return out_path
