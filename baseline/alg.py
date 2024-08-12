import pandas as pd
import numpy as np
def baseline(lengths, replacements, pattern, base_year):
    baseline_lengths = []
    valid_indices = []
    num_slabs = len(lengths)
    bsid = [None for _ in range(num_slabs)]
    for i in range(num_slabs):
        if (replacements[i] != 'R'
            and (i == 0 or replacements[i-1] != 'R') 
            and (i == len(lengths) - 1 or replacements[i+1] != 'R')):

            valid_indices.append(i)
    print(valid_indices)
    for i in range(len(valid_indices)):
        curr_index = valid_indices[i]
        if i == 0 or valid_indices[i - 1] == curr_index - 1:
            baseline_lengths.append(lengths[curr_index])
            
        else:
            r = curr_index
            l = valid_indices[i - 1]
            replacement_lengths = lengths[l+1:r]
            baseline_lengths += generate_baseline_lengths(replacement_lengths, pattern)
            baseline_lengths.append(lengths[curr_index])
        bsid[curr_index] = len(baseline_lengths)
    return baseline_lengths, bsid



def generate_baseline_lengths(replacement_lengths, pattern):
    pattern_avg = sum(pattern) / len(pattern)   
    est_slabs = round(sum(replacement_lengths) / pattern_avg)
    baseline_lengths = [0 for i in range(est_slabs)]
    

    return baseline_lengths

df = pd.read_excel('lengths.xlsx')
lengths = df['BY_length (ft)'].tolist()
replacements = df['2013_state'].tolist()
pattern = [16, 17, 22, 23]
# lengths = [21.88, 23.29, 17.49, 16.57, 21.82, 9.49, 13.23, 8.9, 9.03, 22, 23]
# rep = [0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0]

baseline_lengths, bsid = baseline(lengths, replacements, pattern, 2013)

df['bsid'] = bsid

df.to_excel('baseline_lengths.xlsx')