import pandas as pd
import numpy as np
def baseline(lengths, replacements, pattern, BYID_start):
    baseline_lengths = []
    valid_indices = []
    num_slabs = len(lengths)
    bsid = [None for _ in range(num_slabs)]
    byid = []
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
            byid.append(curr_index + BYID_start)
            
        else:
            r = curr_index
            l = valid_indices[i - 1]
            replacement_lengths = lengths[l+1:r]
            baseline_lengths += generate_baseline_lengths(replacement_lengths, pattern, byid)
            baseline_lengths.append(lengths[curr_index])
            byid.append(curr_index + BYID_start)
        bsid[curr_index] = len(baseline_lengths)
    return baseline_lengths, bsid, byid



def generate_baseline_lengths(replacement_lengths, pattern, byid):
    pattern_avg = sum(pattern) / len(pattern)   
    est_slabs = round(sum(replacement_lengths) / pattern_avg)
    baseline_lengths = [sum(replacement_lengths) / est_slabs for i in range(est_slabs)]
    for _ in range(len(baseline_lengths)):
        byid.append(None)
    return baseline_lengths

df = pd.read_excel('lengths.xlsx')
lengths = df['BY_length (ft)'].tolist()
replacements = df['2013_state'].tolist()
pattern = [16, 17, 22, 23]
# lengths = [21.88, 23.29, 17.49, 16.57, 21.82, 9.49, 13.23, 8.9, 9.03, 22, 23]
# rep = [0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0]

baseline_lengths, bsid, byid = baseline(lengths, replacements, pattern, 8)
df_1 = pd.DataFrame()
df_1['baseline_lengths'] = baseline_lengths
df_1['byid'] = byid
df_1['bsid'] = [i for i in range(1, len(baseline_lengths) + 1)]
df['bsid'] = bsid
df.to_excel('baseline_lengths.xlsx')
df_1.to_excel('baseline_lengths_and_BYID.xlsx', index=False)