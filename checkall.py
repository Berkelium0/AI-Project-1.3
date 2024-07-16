import requests
import sys
import pathlib
import json

solpath = pathlib.Path(sys.argv[1])



def read(file):
    with open(file) as fp:
        return fp.read()

correct = 0
wrong = 0

for solution_path in solpath.glob('*.solution'):

    clues = read(pathlib.Path(__file__).parent / 'clues' / solution_path.name.replace('solution', 'clues'))
    clue_lines = clues.splitlines()

    data = {
        'goal': 'check',
        'clues': clues,
        # solution file format is different on the server
        'solution': 'anonymous problem\n' + clue_lines[0].split()[0] + '\n' + clue_lines[1] + '\n' + read(solution_path).replace('-', '0').replace('a', '1').replace('b', '2').replace('c', '3'),
    }

    response = requests.get(f'http://jfschaefer.de:8973/verify/ss23a31a/nonograms', data=json.dumps(data))
    print(solution_path.name)
    print('   ', response.text)
    if response.text == 'Correct':
        correct += 1
    else:
        wrong += 1

print()
print(f'Correct: {correct}, Wrong: {wrong}')
