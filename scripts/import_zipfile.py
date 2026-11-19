import zipfile
import pandas as pd
from pathlib import Path

def read_hh(zip_file):
    zip_file = Path(zip_file)

    keep = [
        "TIMESTAMP_START", "TIMESTAMP_END", "TA_F", "SW_IN_F", "VPD_F", "P_F",
        "NETRAD", "G_F_MDS", "H_F_MDS", "H_F_MDS_QC", "LE_F_MDS", "LE_F_MDS_QC",
        "NEE_VUT_REF", "NEE_VUT_REF_QC", "GPP_NT_VUT_REF", "RECO_NT_VUT_REF"
    ]

    with zipfile.ZipFile(zip_file) as z:
        hh_names = [n for n in z.namelist() if "FLUXMET_HH" in n]
        if not hh_names:
            raise ValueError(f"No FLUXMET_HH file found in {zip_file}")

        with z.open(hh_names[0]) as f:
            hh = pd.read_csv(
                f,
                na_values=[-9999],
                usecols=lambda c: c in keep,
                dtype={"TIMESTAMP_START": str,
                       "TIMESTAMP_END": str}
            )

    hh["time"] = pd.to_datetime(
        hh["TIMESTAMP_START"],
        format="%Y%m%d%H%M"
    )

    hh["site"] = zip_file.stem.split("_")[1]
    return hh


def read_all_hh(data_dir=Path("data/raw")):
    zip_files = sorted(Path(data_dir).glob("*_FLUXNET_*.zip"))
    if not zip_files:
        raise FileNotFoundError(f"No FLUXNET zip files found in {data_dir}")
    return pd.concat([read_hh(zip_file) for zip_file in zip_files], ignore_index=True)


if __name__ == "__main__":
    hh_all = read_all_hh()
    print(hh_all.head())
    print(hh_all["site"].unique())
    print(hh_all.shape)
    print(hh_all.groupby("site").size())