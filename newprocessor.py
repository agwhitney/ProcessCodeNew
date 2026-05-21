"""
The existing processing method has nearly a dozen steps with a bunch of code editing and idiosyncracies.
This code should hopefully streamline some of that process. 
Adam Whitney May 2026
"""
from pathlib import Path

from Reader.ProccessMeasurementsL1a import process
from Reader.Calibration.Cal_Step_1_MW import calstep1
from Reader.Calibration.Cal_Step_2_MW import calstep2


def make_csv(source_dir: Path, output_filename: Path) -> None:
    with open(output_filename, 'w') as file:
        for p in source_dir.iterdir():
            if p.suffix == '.h5':
                file.write(str(p) + '\n')
        file.write("SacrificialLine")
    return


def move_file(source_filename: Path, output_dir: Path) -> Path:
    source_filename.rename(output_dir / source_filename.name)
    print(f"Moved\n{source_filename}\nto\n{output_dir}")
    return output_dir / source_filename.name


def main():
    L0b_files = Path.cwd() / 'L0bFiles'
    # STEP 1a - Put the data that will be used to calibrate (i.e., LN2 data) into L0bFiles/Calibration
        # NOTE 3 or more files are required for calibration
    # STEP 1b - Put the data that you want calibrated into L0bFiles/Data
    ln2_dir = L0b_files / 'Calibration'
    data_dir = L0b_files / 'Data'


    # STEP 2 - Make batch.csv files for the calibration and scene data
    csv_output_dir = Path.cwd() / 'Reader/CSV batch files'
    make_csv(ln2_dir, csv_output_dir / 'ln2.csv')
    make_csv(data_dir, csv_output_dir / 'all.csv')


    # STEP 3 - Run Cal_Step_1
    # Output goes to Reader/Results/L0bdata in folders for each file and one named 'ln2CVS'.
    ln2_filepaths = list(f for f in ln2_dir.iterdir() if f.suffix == '.h5')
    calstep1(ln2_filepaths)


    # STEP 4 - Run Cal_Step_2. 
    # Output is a bunch of figures in ln2CVS from above, and a TREC.csv file
    # That file needs to get moved to Reader/Calibration folder
    calstep2()
    calstep2_output_dir = Path.cwd() / 'Reader/Results/L0bdata/ln2CVS'
    calibration_dir = Path.cwd() / 'Reader/Calibration'
    for path in calstep2_output_dir.iterdir():
        if path.name.find('Trec') != -1 and path.suffix == '.csv':
            trec_filepath = path
    new_trec_filepath = move_file(trec_filepath, calibration_dir)


    # STEP 5 - Run 'Proccess Measurements L1a.py' from the root folder
    process(channelset='mw', trec_filename=new_trec_filepath, seconds_to_analyze=300, batch_filename='all')


if __name__ == '__main__':
    main()
    # process(channelset='mw', trec_filename='Reader/Calibration/2026_05_13_0001_20_ln2_test_LN2_Trec_model_mw.csv', seconds_to_analyze=300, batch_filename='all')