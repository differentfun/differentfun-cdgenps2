# differentfun-cdgenps2

A modern, Python-based reimplementation of the classic CDGenPS2 tool for PlayStation 2.
This project is aimed at educational and research purposes, helping developers build and test homebrew PS2 software.
The goal is not to clone CDGenPS2, but simply to provide a way for users to create bootable ISO images with custom .ELF files.
This is especially useful for those who want to develop and run their own software on real PS2 hardware or emulators.

---

## ⚠️ Disclaimer

This software is provided **strictly for educational and non-commercial purposes**.

- It is **not affiliated with, endorsed by, or associated with Sony Computer Entertainment Inc.** or any of its subsidiaries.
- It must **not** be used to create, distribute, or facilitate the distribution of copyrighted material.
- The author does **not condone** piracy or any illegal use of this tool.
- By using this software, **you agree** to comply with all applicable laws and regulations in your country or region.
- The developer of this tool is not responsible for how it is used. Users are solely responsible for ensuring their use of the software complies with all applicable laws and ethical standards.
 
---

## 🎯 Intended Use

This tool is designed for:
- Developers creating and testing **homebrew** applications for PlayStation 2.
- Researchers or enthusiasts exploring how PS2 disc structures and bootable ISOs work.
- Educational exploration of old console development practices using modern Python code.

This project **is not** intended for:
- Running or copying commercial games.
- Circumventing copy protection mechanisms.
- Any activity that violates intellectual property laws.

---

## 🧬 Status Informations

- The tool is in Alpha, it has been tested with uLaunchELF and works but you have to disable the FastBoot 
- Full boot will make the generated iso work with no problems 

---

## 🛠 Features

- Add individual files or entire folders to an ISO image structure.
- Set a custom `BOOT.ELF` file for launching on PS2.
- Generate standard ISO images with `genisoimage` usable with emulators or real hardware.
- CLI-driven with a minimal GUI available.

---

## 🖼️ Screenshot

![Example](https://i.imgur.com/Xq1zlli.png)

---

## 📄 License

This project is licensed under the **GNU General Public License v3.0 (GPL-3.0)**.  
See the `LICENSE` file for full legal terms.

---


## 🐍 Requirements

- Python 3.11+
- See `requirements.txt` for required packages.
- As linux dependencies: libxcb1 libx11-xcb1 libxcb-render0 libxcb-shape0 libxcb-xfixes0 libxcb-cursor0 libxcb-icccm4 libxcb-image0 libxcb-keysyms1 libxcb-randr0 libxcb-render-util0 libxcb-xinerama0

You can install dependencies via:

```bash
bash install_libraries.sh
```

---

## 🚀 Usage
1. Clone this repo:
   ```bash
   git clone https://github.com/differentfun/differentfun-cdgenps2
   ```
   ```bash
   cd differentfun-cdgenps2
   ```

2. Install the dependencies (works only on debian based distros)
   ```bash
   bash install_libraries.sh
   ```

3. Set-up virtual environment
   ``` bash
   ./setup_env.sh
   ```

4. Run the tool
   ```bash
   ./run_cdgenps2.sh
   ```
5. Iso construction

   Insert the needed files, then select the .ELF that has to boot
   Then click on `Set as Main ELF boot`, this will generate the SYSTEM.CNF with the boot informations.
   
7. You're done

   Now you can build the ISO.

## 🙏 Acknowledgements

Inspired by the original CDGenPS2 utility.

---
