# 🧠 Ultra Sound Video Frame Annotation Tool

**A privacy-preserving, open-source web-based tool for frame-by-frame annotation of ultrasonic video data.**  
Ideal for creating machine learning datasets in medical imaging — especially for liver cancer classification tasks like HCC vs. CCC.

---

## 🔍 Overview

This tool provides an intuitive browser-based interface to:

- ✅ Import and process `.avi` ultrasonic video files.
- 🧼 Automatically crop frames to remove sensitive patient information.
- 🖍️ Manually annotate frames for use in supervised learning tasks.
- 🧾 Export structured datasets ready for machine learning pipelines.

Designed with **GDPR compliance** in mind, all processing is done locally — no data ever leaves your machine.

---

## 📌 Key Features

- **Fully local + open source**  
  No licenses or server dependencies. Completely free and private by design.

- **Automatic De-identification**  
  Crops videos to exclude patient-identifying metadata or overlays.

- **Frame-by-frame Annotation**  
  Annotate each frame with labels (e.g., HCC / CCC). Annotation schema is easily customizable.

- **Export Dataset**  
  Generates labeled datasets compatible with ML frameworks (e.g., PyTorch, TensorFlow).

- **Easy to Use**  
  Lightweight interface with clear navigation. Launches in your browser with a single command.

---

## 🛠️ Installation

### 🔧 Requirements

- Python 3.8+
- pip

### 📦 Setup Instructions

Clone the repository:

```bash
git clone https://github.com/V-Sehra/Ultra_sound_annotation.git
cd Ultra_sound_annotation

