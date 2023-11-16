import json
import matplotlib.pyplot as plt
import os
import pandas as pd
import seaborn as sns


def plot_gas_usage():
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
                gas_used[operation].append(sum(user_gas_used[operation]) / len(user_gas_used[operation]))

            dem_gas_used = {}
            dem_gas = data['dem_gas']
            for operation, gas in dem_gas.items():
                if operation not in dem_gas_used:
                    dem_gas_used[operation] = []
                dem_gas_used[operation].append(gas)
            dem_gas_list.append(dem_gas_used)

    # Creating bar plots using seaborn
    df = pd.DataFrame(gas_used, index=num_users_list).reset_index().melt(id_vars='index', var_name='Operation',
                                                                         value_name='Gas Usage')
    plt.figure(figsize=(10, 6))
    sns.barplot(data=df, x='index', y='Gas Usage', hue='Operation')
    plt.title('Gas Usage by Operation and Number of Users')
    plt.ylabel('Gas Usage')
    plt.xlabel('Number of Users')
    plt.legend(title='Operation')
    plt.tight_layout()

    bar_plot_path = os.path.join(directory, 'gas_usage_bar.png')
    plt.savefig(bar_plot_path)
    plt.show()
    return bar_plot_path


# Call the function to create the bar plot
plot_gas_usage()

# import json
# import matplotlib.pyplot as plt
# import os
#
# import numpy as np
#
# # This is the directory where the JSON files are stored
# #  get the current working directory
# def plot_gas_usage():
#     directory = os.getcwd()
#     # This is a dictionary to store the gas used for each operation for each number of users
#     gas_used = {}
#     gas_used_list = []
#     dem_gas = {}
#     dem_gas_list = []
#
#
#
#     # This is a list to store the number of users for which we have data
#     num_users_list = []
#
#     # Iterate over each file in the directory
#     for filename in os.listdir(directory):
#         if filename.endswith('.json'):
#             # Load the data from the file
#             with open(os.path.join(directory, filename), 'r') as f:
#                 data = json.load(f)
#             #  For user perspective
#             num_users = data['num_users']
#             num_users_list.append(num_users)
#             user_gas_used = {}
#             user_gas_total = data['user_gas_total']
#             for user in user_gas_total:
#                 for operation, gas in user.items():
#                     if operation not in user_gas_used:
#                         user_gas_used[operation] = []
#                     user_gas_used[operation].append(gas)
#             for operation in user_gas_used:
#             #      compute the average gas used for each operation
#                 if operation not in gas_used:
#                     gas_used[operation] = []
#                 gas_used[operation]= sum(user_gas_used[operation]) / len(user_gas_used[operation])
#             gas_used_list.append(gas_used)
#     #          #  For DEM perspective
#             dem_gas_used = {}
#             dem_gas = data['dem_gas']
#             for operation, gas in dem_gas.items():
#                 if operation not in dem_gas_used:
#                     dem_gas_used[operation] = []
#                 dem_gas_used[operation].append(gas)
#             dem_gas_list.append(dem_gas_used)
#
#
#     # Plot the gas used for each operation
#     plot_data = {}
#     for i in range(len(gas_used_list)):
#         for operation, gas in gas_used_list[i].items():
#             if operation not in plot_data:
#                 plot_data[operation] = []
#             plot_data[operation].append(gas)
#
#     for operation in plot_data:
#         plt.plot(num_users_list, np.array(plot_data[operation])/1e3, label=operation )
#         plt.xlabel('Number of users')
#         plt.ylabel('Gas used in thousands')
#         plt.legend()
#
#     plot_data_dem = {}
#     for i in range(len(dem_gas_list)):
#         for operation, gas in dem_gas_list[i].items():
#             if operation not in plot_data_dem:
#                 plot_data_dem[operation] = []
#             plot_data_dem[operation].append(gas)
#     for operation in plot_data_dem:
#         plt.plot(num_users_list, np.array(plot_data_dem[operation])/1e3, label=operation )
#         plt.xlabel('Number of users')
#         plt.ylabel('Gas used in thousands')
#         plt.ylim(0, 450)
#         #  change the pisition of the legend to bottom right
#         plt.legend(loc='upper right')
#     image_path = os.path.join(directory, 'gas_usage.png')
#     plt.savefig('gas_usage.png')
#     plt.show()
#     return image_path
#
#
#
