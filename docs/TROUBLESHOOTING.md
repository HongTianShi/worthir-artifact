# Troubleshooting

## Confirm which installation you are using

Run:

```bash
python --version
python -m worthir doctor
```

WorthIR requires Python 3.10 or newer. `python -m worthir` is the most reliable
entry when a globally installed `worthir` command is not on `PATH`.

## The source launcher cannot find or use `.venv`

The source launchers create `.venv` in the repository. Moving the repository
can leave that environment with paths to its old location. Delete only the
repository's `.venv` directory and run the launcher again:

```powershell
Remove-Item -LiteralPath .venv -Recurse
.\worthir.cmd doctor
```

```bash
rm -rf .venv
./worthir doctor
```

Rebuild `.venv` when its Python executable is missing, the repository was
moved, or package imports fail immediately after a Python upgrade. Do not
delete it for an evaluator validation error; fix the task files instead.

## Windows opens the wrong Python

Use `py -3.13 -m pip install worthir-eval==1.3.0` and
`py -3.13 -m worthir doctor`, replacing `3.13` with an installed Python version.
The Microsoft Store alias can be disabled under **Manage app execution
aliases** if it intercepts `python`.

## PyPI installation cannot reach the package index

Check that the same interpreter can reach PyPI:

```bash
python -m pip install --index-url https://pypi.org/simple worthir-eval==1.3.0
```

On a managed network, use the proxy or package index approved by the local
administrator. The source launcher still needs access to PyPI when it creates
`.venv`.

## Hugging Face or dataset downloads fail

The core evaluator does not download models. Full route rebuilds may use
Hugging Face or official dataset hosts. Retry the task's `prepare` stage before
running routes. For FiQA:

```bash
python paper_results/full_replay/replay.py fiqa260 prepare --workspace fiqa-work
```

If a model host is blocked, download the named checkpoint through an approved
network and point the task adapter at that local directory. Do not substitute a
different model without recording the change.

## Disk space or cache location

`worthir demo-custom` is small. Full replay is not: model caches, corpora, and
indexes can require several gigabytes. Check the task card in
`paper_results/full_replay/RESOURCE_REQUIREMENTS.md` first. Hugging Face caches
can be moved by setting `HF_HOME` to a drive with enough free space before
download.

## A task fails validation

Run `worthir validate-task TASK --output validation.json`. The report checks
query and route coverage, prerequisite closure, cumulative costs, public cost
consistency, and the information boundary. Do not rebuild the Python
environment for a missing query--route pair or malformed contract.

## Report a reproducible bug

Use the repository's **Bug report** issue form. Include the command, Python and
operating-system versions, the full error, and whether the PyPI package or a
source checkout was used. Do not attach evaluator ledgers that cannot be
redistributed.
