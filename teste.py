import glob

files = glob.glob("enem-experiments-results/llama2-13b-.*")
files = [f for f in files if "full-answers" not in f]

files.sort()

print(len(files))