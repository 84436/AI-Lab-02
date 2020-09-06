from copy import deepcopy
from itertools import product, groupby
import os

##########

def neg(x):
    if '-' in x:
        return x.replace('-', '')
    else:
        return '-' + x

def parse(file_object):
    lines = []
    alpha = []
    kb = []
    alpha_count = 0
    kb_count = 0
    lines = file_object.read().splitlines()
    alpha_count = int(lines.pop(0))
    while alpha_count > 0:
        l = lines.pop(0)
        l = [[c.strip() for c in l.split(' OR ')]]
        alpha.extend(l)
        alpha_count -= 1
    kb_count = int(lines.pop(0))
    while kb_count > 0:
        l = lines.pop(0)
        l = [[c.strip() for c in l.split(' OR ')]]
        kb.extend(l)
        kb_count -= 1
    return alpha, kb

def neg_alpha(alpha):
    r = []
    for each in alpha:
        r.append([neg(c) for c in each])
    r = list(product(*r))
    r2 = []
    for i, each in enumerate(r):
        if all(neg(each_c) not in each for each_c in each):
            r2.append(each)
    r = r2
    r = [
        sorted(set(each), key=lambda c: c.replace('-', '') if '-' in c else c)
        for each in r
    ]
    r = list(each for each, _ in groupby(sorted(r)))
    return r

def resolve(a, b):
    len_total = len(a) + len(b)
    r = a + b
    for each in r:
        if neg(each) in r:
            r.remove(each)
            r.remove(neg(each))
            break
    for each in r:
        if neg(each) in r:
            return None
    if len(r) == len_total:
        return None
    r = set(r)
    r = sorted(r, key=lambda c: c.replace('-', '') if '-' in c else c)
    r = list(r)
    return r

def iterate(input_kb, verbose=False):
    kb       = deepcopy(input_kb)
    kb_check = deepcopy(input_kb)
    yields   = []
    for each_a in kb:
        kb_no_each = deepcopy(kb)
        kb_no_each.remove(each_a)
        for each_b in kb_no_each:
            r = resolve(each_a, each_b)
            isNone    = r is None
            isInKB    = None
            isInYield = None
            if (not isNone):
                isInKB    = (r in kb_check or list(reversed(r)) in kb_check)
                isInYield = (r in yields   or list(reversed(r)) in yields)
            if verbose:
                status = '-'
                if isInKB: status = 'k'
                if isInYield: status = 'y'
                print('{s} {a} + {b} -> {r}'.format(
                    s=status, a=each_a, b=each_b, r=r
                ))
            if (not isNone) and (not isInKB) and (not isInYield):
                yields.extend([r])
    return yields

def run(input_kb, input_alpha, verbose=False, verbose_iterate=False, write_to_file=False):
    global filename
    if write_to_file:
        f = open(output_file(filename), mode='w+', newline='\n')
    kb = deepcopy(input_kb)
    alpha = deepcopy(input_alpha)
    kb.extend(neg_alpha(alpha))
    it = 0
    if verbose:
        print('Initial KB:')
        for i, each in enumerate(kb): print('{}: {}'.format(i, each))
        print()
    while True:
        if verbose:
            print('Iteration', it)
        y = iterate(kb, verbose_iterate)
        if verbose:
            if len(y) > 0:
                print('yield length =', len(y))
                for i, each in enumerate(y): print('{}: {}'.format(i, each))
            else:
                print('empty yield')
        if write_to_file:
            f.write('{}'.format(len(y)))
            f.write('\n')
            for each in y:
                if each == []:
                    f.write('{}')
                    f.write('\n')
                else:
                    f.write(' OR '.join(each))
                    f.write('\n')
        kb.extend(y)
        if [] in kb:
            if verbose:
                print('YES')
            if write_to_file:
                f.write('YES')
                f.close()
            break
        if len(y) == 0:
            if verbose:
                print('NO')
            if write_to_file:
                f.write('NO')
                f.close()
            break
        if verbose:
            print()
        it += 1

##########

if __name__ == '__main__':
    BASE_DIR   = os.path.dirname(os.path.realpath(__file__)) + '/..'
    INPUT_DIR  = BASE_DIR + '/input'
    OUTPUT_DIR = BASE_DIR + '/output'
    input_file  = lambda filename: INPUT_DIR + '/' + filename
    output_file = lambda filename: OUTPUT_DIR + '/' + filename

    alpha, kb, filename = None, None, None
    filelist = tuple(*os.walk(INPUT_DIR))[2]
    for each_file in filelist:
        filename = each_file
        with open(input_file(filename), 'r') as f:
            alpha, kb = parse(f)
        run(kb, alpha, verbose=False, verbose_iterate=False, write_to_file=True)
        print('Done:', filename)
