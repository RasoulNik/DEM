import json
import matplotlib.pyplot as plt
import os
import numpy as np

directory = os.getcwd()
gas_used = {}
gas_used_list = []
dem_gas = {}
dem_gas_list = []

num_users_list = []

for filename in os.listdir(directory):
    if filename.endswith('.json'):
        with open(os.path.join(directory, filename), 'r') as f:
            data = json.load(f)
        num_users = data['num_users']
        num_users_list.append(num_users)
        user_gas_used = {}
        user_gas_total = data['user_gas_total']
        for user in user_gas_total:
            for operation, gas in user.items():
                if operation not in user_gas_used:
                    user_gas_used[operation] = []
                user_gas_used[operation].append(gas)
        for operation in user_gas_used:
            if operation not in gas_used:
                gas_used[operation] = []
            gas_used[operation] = sum(user_gas_used[operation]) / len(user_gas_used[operation])
        gas_used_list.append(gas_used)
        dem_gas_used = {}
        dem_gas = data['dem_gas']
        for operation, gas in dem_gas.items():
            if operation not in dem_gas_used:
                dem_gas_used[operation] = []
            dem_gas_used[operation].append(gas)
        dem_gas_list.append(dem_gas_used)

bar_width = 0.35
index = np.arange(len(num_users_list))
plot_data = {}
for i in range(len(gas_used_list)):
    for operation, gas in gas_used_list[i].items():
        if operation not in plot_data:
            plot_data[operation] = []
        plot_data[operation].append(gas)

fig, ax = plt.subplots()
for idx, operation in enumerate(plot_data):
    ax.bar(index + idx*bar_width, np.array(plot_data[operation])/1e3, bar_width, label=operation)

plot_data_dem = {}
for i in range(len(dem_gas_list)):
    for operation, gas in dem_gas_list[i].items():
        if operation not in plot_data_dem:
            plot_data_dem[operation] = []
        plot_data_dem[operation].append(gas)

for idx, operation in enumerate(plot_data_dem):
    ax.bar(index + len(plot_data)*bar_width + idx*bar_width, np.array(plot_data_dem[operation])/1e3, bar_width, label=operation)

ax.set_xlabel('Number of users')
ax.set_ylabel('Gas used in thousands')
ax.set_title('Gas usage by number of users and operation')
ax.set_xticks(index + bar_width / 2)
ax.set_xticklabels(num_users_list)
ax.legend(loc='upper right')
plt.tight_layout()
plt.savefig('gas_usage_bar.png')
plt.show()
