# 📂 File Merger Batch Utility

A companion tool to [`file_merger`](../file_merger) that allows you to merge files in **batches** based on a glob pattern.  
Instead of manually listing files, you can specify a pattern (e.g. `a/*.txt`) and a **chunk size**. The tool will group files into chunks of that size and call `merge_files_with_formatting` for each batch, producing multiple merged outputs.

---

## 📂 Project Structure

```
file_merger_batch/
│
├── __init__.py
├── __main__.py
├── batch_merger.py
├── config.example.yml
└── README.md
```

---

## ⚡ Usage

1. Create a `config.yml` file:

```yaml
files: "a/*.txt"                       # Glob pattern to match input files
first_prepend: "---AT THE BEGINNING---\n"  # Prepended once at the beginning
prefix: "---START---\n"                # Prefix before each file's content
join: "\n---NEXT FILE---\n"            # Separator between files
suffix: "\n---END---\n"                # Suffix after each file's content
final_append: "\n=== ALL FILES MERGED SUCCESSFULLY ===\n"  # Appended once at the end
output_path: "b/c/"                    # Directory to save merged outputs
output_file_name_pattern: "abc[batch].txt"  # [batch] replaced with batch number
chunk_size: 5                          # Number of files per merged batch
```

2. Run the tool:

```bash
python -m file_merger_batch -c config.yml
```

This will:
- Expand the glob pattern (`a/*.txt`)
- Split the files into chunks of 5
- Merge each chunk into a separate file
- Save outputs as `b/c/abc1.txt`, `b/c/abc2.txt`, etc.
- Apply first_prepend, prefix, join, suffix, and final_append formatting

---

## 📦 Features

- Accepts **glob patterns** for flexible file selection.
- Splits files into **configurable batch sizes**.
- Uses the proven `merge_files_with_formatting` function from `file_merger`.
- Configurable formatting via YAML (`first_prepend`, `prefix`, `join`, `suffix`, `final_append`).
- Generates **multiple output files** with customizable naming patterns.
- Efficient streaming (handles large files line by line).

---

## 🔗 Related

- [`file_merger`](../file_merger): Merge multiple files into a single output with formatting.
```
