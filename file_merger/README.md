# 📂 File Merger Utility

A lightweight Python package/CLI tool to merge multiple files into one, with configurable **prefix**, **join string**, and **suffix**.  
Configuration is provided via a YAML file, while file paths are passed as command-line arguments.

---

## 📂 Project Structure

```
file_merger/
│
├── __init__.py
├── __main__.py
├── merger.py
├── config.example.yml
└── README.md
```

---

## ⚡ Usage

1. Create a `config.yml` file:

```yaml
first_prepend: "---AT THE BEGINNING---\n"
prefix: "---START---\n"
join: "\n---NEXT FILE---\n"
suffix: "\n---END---\n"
final_append: "\n=== ALL FILES MERGED SUCCESSFULLY ===\n"
output_path: "merged_output.txt"
```

2. Run the tool:

```bash
python -m file_merger -c config.yml file1.txt file2.txt file3.txt
```

This will produce `merged_output.txt` with:
- A string (`first_prepend`) appended once at the very beginning
- Each file wrapped in `prefix` and `suffix`
- Files separated by `join`
- A final string (`final_append`) appended once at the very end

---

## 📦 Features

- Efficient streaming (handles large files line by line).
- Configurable formatting via YAML.
- Works as both a **library** and a **CLI tool**.
- Easy to extend for automation.
