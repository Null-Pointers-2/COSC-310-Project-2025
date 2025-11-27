from pydriller import Repository
import argparse

parser = argparse.ArgumentParser(description='Search commits by author name')
parser.add_argument('name', type=str)
args = parser.parse_args()

name = args.name
for commit in Repository('https://github.com/Null-Pointers-2/COSC-310-Project-2025.git').traverse_commits():
    if name in commit.author.name:
        print('Hash {}, author {}'.format(commit.hash, commit.author.name), commit.lines)
