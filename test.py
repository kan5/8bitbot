import json

user_states = {0: {'required_name': '', 'state': 0, 'style': 'NES', 'width': 'most'}}

with open('user_states.json', 'w') as fp:
    json.dump(user_states, fp)

user_states[0] = 1
with open('user_states.json', 'r') as fp:
    user_states = json.load(fp)
print(user_states)