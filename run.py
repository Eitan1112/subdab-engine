import numpy as np
import math
starts_range = np.arange(120,125,0.2)
def trim(sorted_results):
    final_ids_times = []
    # Loop through combos of result and next result
    for result, next_result in zip(sorted_results[:-1], sorted_results[1:]):
        
        # If the next result is more then the trim step -> continue (it happends because of the threading)
        if(math.isclose(next_result['start'] - result['start'], 0.2) is False): # Using math.isclose becuase the equality is falty in float numbers
            print('not close', next_result['start'] - result['start'])
            continue
        
        # If the final trimmed section also has the hot word present, add it
        if(next_result['start'] == starts_range[-1]):
            last_section_trimmed_items = [item for item in next_result['ids'] if item['occurences'] > 0]
            final_ids_times += last_section_trimmed_items

        # Grab items where the id's correlate and the occurences are at least 1 for the first and 0 for the next
        final_item = [item for item in result['ids'] for next_item in next_result['ids'] if item['id'] == next_item['id'] and item['occurences'] > 0 and next_item['occurences'] == 0]
        print(final_item)
        if(len(final_item) > 0):
            final_ids_times.append({'id': final_item[0]['id'], 'start': result['start']})
        print(final_ids_times)

        if(len(final_ids_times) == 1):
            print('finished')
            stop = True
            print(f'Final ids times returened: {final_ids_times}. Results: {sorted_results}')
            return final_ids_times
        

results = [{'start': 120.0, 'end': 125, 'ids': [{'id': 'stood-af7502', 'occurences': 2}]}, {'start': 120.2, 'end': 125, 'ids': [{'id': 'stood-af7502', 'occurences': 1}]}, {'start': 120.4, 'end': 125, 'ids': [{'id': 'stood-af7502', 'occurences': 1}]}, {'start': 120.80000000000001, 'end': 125, 'ids': [{'id': 'stood-af7502', 'occurences': 2}]}, {'start': 121.00000000000001, 'end': 125, 'ids': [{'id': 'stood-af7502', 'occurences': 1}]}, {'start': 121.20000000000002, 'end': 125, 'ids': [{'id': 'stood-af7502', 'occurences': 2}]}, {'start': 121.40000000000002, 'end': 125, 'ids': [{'id': 'stood-af7502', 'occurences': 2}]}, {'start': 121.60000000000002, 'end': 125, 'ids': [{'id': 'stood-af7502', 'occurences': 1}]}, {'start': 121.80000000000003, 'end': 125, 'ids': [{'id': 'stood-af7502', 'occurences': 2}]}, {'start': 122.00000000000003, 'end': 125, 'ids': [{'id': 'stood-af7502', 'occurences': 1}]}, {'start': 122.20000000000003, 'end': 125, 'ids': [{'id': 'stood-af7502', 'occurences': 1}]}, {'start': 122.40000000000003, 'end': 125, 'ids': [{'id': 'stood-af7502', 'occurences': 1}]}, {'start': 122.60000000000004, 'end': 125, 'ids': [{'id': 'stood-af7502', 'occurences': 1}]}, {'start': 122.80000000000004, 'end': 125, 'ids': [{'id': 'stood-af7502', 'occurences': 1}]}, {'start': 123.00000000000004, 'end': 125, 'ids': [{'id': 'stood-af7502', 'occurences': 1}]}, {'start': 123.20000000000005, 'end': 125, 'ids': [{'id': 'stood-af7502', 'occurences': 1}]}, {'start': 123.40000000000005, 'end': 125, 'ids': [{'id': 'stood-af7502', 'occurences': 1}]}, {'start': 123.60000000000005, 'end': 125, 'ids': [{'id': 'stood-af7502', 'occurences': 0}]}, {'start': 123.80000000000005, 'end': 125, 'ids': [{'id': 'stood-af7502', 'occurences': 0}]}, {'start': 124.00000000000006, 'end': 125, 'ids': [{'id': 'stood-af7502', 'occurences': 0}]}, {'start': 124.20000000000006, 'end': 125, 'ids': [{'id': 'stood-af7502', 'occurences': 0}]}, {'start': 124.40000000000006, 'end': 125, 'ids': [{'id': 'stood-af7502', 'occurences': 0}]}, {'start': 124.60000000000007, 'end': 125, 'ids': [{'id': 'stood-af7502', 'occurences': 0}]}, {'start': 124.80000000000007, 'end': 125, 'ids': [{'id': 'stood-af7502', 'occurences': 0}]}]


print(trim(results))
