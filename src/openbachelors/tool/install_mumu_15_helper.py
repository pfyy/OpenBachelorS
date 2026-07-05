import subprocess

from tkinter.filedialog import askopenfilenames


def main():
    exe_filepath_lst = askopenfilenames(
        filetypes=[("MUMU 15 Setup", ".exe")],
    )

    exe_filepath_lst = list(exe_filepath_lst)
    exe_filepath_lst.sort(key=lambda exe_filepath: exe_filepath.find("-nxmain-") != -1)

    for exe_filepath in exe_filepath_lst:
        subprocess.run(
            f'"{exe_filepath}" /txn_id=00000000-0000-0000-0000-000000000000 /from_orchestrator=1 /action=install_prepare /auto_start=false /product_version=6.2.3.0 /D=C:\\Program Files\\Netease\\MuMuPlayer',
            shell=True,
        )
        subprocess.run(
            f'"{exe_filepath}" /txn_id=00000000-0000-0000-0000-000000000000 /from_orchestrator=1 /action=commit /auto_start=false /product_version=6.2.3.0 /D=C:\\Program Files\\Netease\\MuMuPlayer',
            shell=True,
        )


if __name__ == "__main__":
    main()
