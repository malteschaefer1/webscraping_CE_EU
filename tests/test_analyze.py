import pandas as pd
from unittest.mock import patch

from analyze import generate_plots


def test_generate_plots_creates_expected_files(tmp_path):
    df = pd.DataFrame(
        {
            "Country": ["Belgium", "France", "Belgium"],
            "Scope": ["National", "Local", "National"],
        }
    )
    output_dir = tmp_path / "plots"

    def _fake_save_bar_plot(_, column: str, filename):
        filename.write_text(f"plot for {column}")

    with patch("analyze.save_bar_plot", side_effect=_fake_save_bar_plot):
        generate_plots(df, ["Country", "UnknownColumn"], output_dir)

    expected_file = output_dir / "Country_distribution.png"
    missing_file = output_dir / "UnknownColumn_distribution.png"
    assert expected_file.exists()
    assert not missing_file.exists()
