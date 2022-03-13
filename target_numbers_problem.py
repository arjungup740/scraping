## given a list of numbers, see if you can return the 2 indices that sum to a target number
## O(n^2) solution -- loop through each index, go through the future indices, see if the numbers sum
## O(n) -- go through each number, subtract from target and get its complement

num_list = [2,3,6,1,8]
target = 11
dict_of_complements = {}
def find_indices_that_sum_to_target(num_list, target):
    for index, initial_element in enumerate(num_list):
        complement = target - initial_element
        dict_of_complements[complement] = [initial_element, index]
        if initial_element in dict_of_complements.keys():
            return f'The value = {initial_element} at index {index} and value = {dict_of_complements[initial_element][0]} at index {dict_of_complements[initial_element][1]} sum to {target}'
    ## if end up not finding anything
    return 'nothing sums'

result = find_indices_that_sum_to_target(num_list, target)
print(result)
