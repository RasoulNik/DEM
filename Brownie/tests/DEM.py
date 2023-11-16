from flask import Flask, jsonify
from brownie import project, network, accounts
import json

# Load your Brownie project
p = project.load('../../DEM_brownie', name="DEM_brownie")
p.load_config()

# Import your contract classes
from brownie.project.DEM_brownie import (EnergyProfile, EnergyPool, EnergyMarket, MockV3AggregatorEnergyProduced,
                                         MockV3AggregatorEnergyConsumed, MockV3AggregatorPrice)

# Connect to the network and set the number of accounts in the ganache to 100


network.connect('ganache')
#network.connect('development')

#  Define a class to keep track of the deployed contracts and latest state
class DEM():
    def __init__(self):
        self.energy_profile = None
        self.energy_pool = None
        self.energy_market = None
        self.energy_produced_oracle = None
        self.energy_consumed_oracle = None
        self.energy_price_oracle = None
        self.Gas_used = []
#      get the address of the deployed contract
    def get_address(self):
        return {"energy_profile": self.energy_profile.address, "energy_pool": self.energy_pool.address, "energy_market": self.energy_market.address}
    def set_address(self, energy_profile, energy_pool, energy_market):
        self.energy_profile = energy_profile
        self.energy_pool = energy_pool
        self.energy_market = energy_market

    def deploy(self):
        deployer = network.accounts[0]
        energy_produced_oracle = MockV3AggregatorEnergyProduced.deploy(18, 1000000000, {"from": deployer})
        energy_consumed_oracle = MockV3AggregatorEnergyConsumed.deploy(18, 900000000, {"from": deployer})
        energy_price_oracle = MockV3AggregatorPrice.deploy(18, 1 * 10 ** 14, {"from": deployer})

        energy_profile = EnergyProfile.deploy(
            energy_produced_oracle.address,
            energy_consumed_oracle.address,
            energy_price_oracle.address,
            {"from": deployer},
        )

        energy_market = EnergyMarket.deploy(energy_profile.address, {"from": deployer})

        energy_pool = EnergyPool.deploy(
            energy_profile.address,
            energy_market.address,
            energy_price_oracle.address,
            {"from": deployer},
        )
        energy_profile.setEnergyPoolContract(energy_pool.address, {"from": deployer})
        energy_profile.setEnergyMarketContract(energy_market.address, {"from": deployer})
        energy_market.setEnergyPoolContract(energy_pool.address, {"from": deployer})
        #  set the value of the deployed contract in the dem class
        dem.set_address(energy_profile, energy_pool, energy_market)
        return {"energy_profile": energy_profile.address, "energy_pool": energy_pool.address, "energy_market": energy_market.address}

    def settle_commitment(self):
        # load user 1 and 2 address from accounts
        user1 = network.accounts[1]
        user2 = network.accounts[2]
        value1 = 0.1
        value2 = 0.2
        # # Parse the request data (adjust according to the actual data you're expecting)
        # data = request.get_json()
        # user1 = data['user1']
        # user2 = data['user2']
        # value1 = data['value1']
        # value2 = data['value2']

        # You might need to adjust this part to use the actual deployed instances of your contracts
        energy_profile, energy_pool, energy_market = dem.energy_profile, dem.energy_pool, dem.energy_market

        # Execute the operations
        energy_profile.registerUser(user1, 10, "Location1", "Solar", {"from": user1, "value": value1 * 10 ** 18})
        energy_profile.registerUser(user2, 10, "Location1", "Solar", {"from": user2, "value": value2 * 10 ** 18})

        tokenId1 = energy_profile.tokenOfOwnerByIndex(user1, 0)
        tokenId2 = energy_profile.tokenOfOwnerByIndex(user2, 0)

        energy_profile.createCommitment(tokenId1, 10, False, 195, {"from": user1})
        energy_profile.createCommitment(tokenId2, 3, True, 195, {"from": user2})
        energy_profile.createCommitment(tokenId2, 4, True, 195, {"from": user2})

        energy_profile.approve(energy_pool.address, tokenId1, {"from": user1})
        energy_profile.approve(energy_pool.address, tokenId2, {"from": user2})

        energy_pool.deposit(tokenId1, {"from": user1})
        energy_pool.deposit(tokenId2, {"from": user2})

        energy_market.settle_commitment({"from": user1})

        return jsonify({"message": "Commitments settled successfully!"})

    def compute_gas(self, num_users=9):
        energy_profile, energy_pool, energy_market = self.energy_profile, self.energy_pool, self.energy_market
        gas_used = {}
        user_gas_total = []

        # Register users and keep track of the gas used
        for i in range(1, num_users + 1):
            user_gas = {}
            user = accounts[i]
            tx = energy_profile.registerUser(user, 10, "Location1", "Solar", {"from": user, "value": 0.01 * 10 ** 18})
            user_gas["registerUser"] = tx.gas_used

            # Get tokenId for the user
            tokenId = energy_profile.tokenOfOwnerByIndex(user, 0)

            # Create a commitment for the user and keep track of the gas used
            tx = energy_profile.createCommitment(tokenId, 10, False, 195, {"from": user})
            user_gas["createCommitment"] = tx.gas_used

            # Approve the EnergyPool contract to manage the user's NFT and keep track of the gas used
            tx = energy_profile.approve(energy_pool.address, tokenId, {"from": user})
            user_gas["approve"] = tx.gas_used

            # Deposit the EnergyProfile NFT into the EnergyPool and keep track of the gas used
            tx = energy_pool.deposit(tokenId, {"from": user})
            user_gas["deposit"] = tx.gas_used

            # Save the user's gas usage to the main dictionary
            user_gas_total.append(user_gas)

        gas_used["user_gas_total"] = user_gas_total
        # Call settle_commitment for the first user and keep track of the gas used
        user1 = accounts[1]
        tx = energy_market.settle_commitment({"from": user1})
        dem_gas = {}
        dem_gas["settle_commitment"] = tx.gas_used

        # Add number of users to the data
        gas_used["num_users"] = num_users
        gas_used["dem_gas"] = dem_gas
        self.Gas_used.append(gas_used)
        # Save the gas used for each operation to disk
        filename = f'gas_used_{num_users}_users.json'
        with open(filename, 'w') as f:
            json.dump(gas_used, f)

        # pdb.set_trace()
#  create an instance of the dem class
dem = DEM()
# dem.deploy()
# dem.compute_gas(num_users = 2)
# dem.deploy()
# dem.compute_gas(num_users = 10)
# dem.deploy()
# dem.compute_gas(num_users = 50)

#------------------------------  Deploy a GUI to interact with DEM
import os

import gradio as gr
from extra_func import plot_gas_usage

# Deploy Contracts
def deploy():
    return dem.deploy()

# Settle Commitment
def settle():
    return dem.settle_commitment()

# Compute Gas
def compute(num_users=0):
    return dem.compute_gas(int(num_users))

# Plot Gas Usage
def plot():
    img_path = plot_gas_usage()
    return "See the gas usage plot below.", img_path

logo_path = os.path.join(os.getcwd(), 'gas_usage.png')
# Create Interfaces for each function
deploy_interface = gr.Interface(fn=deploy, inputs=[], outputs=[gr.components.Textbox(label="Output Message")])
settle_interface = gr.Interface(fn=settle, inputs=[], outputs=[gr.components.Textbox(label="Output Message")])
compute_interface = gr.Interface(fn=compute, inputs=[gr.components.Number(label="Number of Users")], outputs=[gr.components.Textbox(label="Output Message")])
plot_interface = gr.Interface(fn=plot, inputs=[], outputs=[gr.components.Textbox(label="Output Message"), gr.components.Image(type="filepath", label="Gas Usage Plot")])

# Create Tabbed Interface
tabbed_interface = gr.TabbedInterface(
    [deploy_interface, settle_interface, compute_interface, plot_interface],
    ["Deploy", "Settle", "Compute", "Plot"],
    title="DEM GUI",
    # description="A GUI to interact with DEM. You can deploy the contracts, settle commitments, compute gas usage, and plot gas usage.",
    # logo= logo_path
)

tabbed_interface.launch()


# flask_app = Flask(__name__)

# @flask_app.route('/deploy')
# def deploy():
#     return jsonify(dem.deploy())
#
# from flask import Flask, jsonify, request
#
# # Your existing imports and setup code...
#
# @flask_app.route('/settle_commitment', methods=['GET'])
# def settle_commitment():
#     return dem.settle_commitment()
#
#
# if __name__ == '__main__':
#     flask_app.run(debug=True)

# Assuming all your previous Brownie and Flask code is above...

# import tkinter as tk
# from tkinter import messagebox
#
# def deploy_contracts():
#     try:
#         result = dem.deploy()
#         messagebox.showinfo("Success", f"Contracts deployed at {result}")
#     except Exception as e:
#         messagebox.showerror("Error", str(e))
#
# def settle_commitment():
#     try:
#         result = dem.settle_commitment()
#         messagebox.showinfo("Success", result["message"])
#     except Exception as e:
#         messagebox.showerror("Error", str(e))
#
# def compute_gas():
#     try:
#         num_users = int(num_users_entry.get())  # Retrieve number from input field
#         dem.compute_gas(num_users)
#         messagebox.showinfo("Success", f"Gas computed for {num_users} users")
#     except Exception as e:
#         messagebox.showerror("Error", str(e))
#
# # Initialize the main window
# root = tk.Tk()
# root.title("Brownie Deployment GUI")
#
# # GUI Elements
# deploy_button = tk.Button(root, text="Deploy Contracts", command=deploy_contracts)
# deploy_button.pack(pady=15)
#
# settle_button = tk.Button(root, text="Settle Commitment", command=settle_commitment)
# settle_button.pack(pady=15)
#
# num_users_label = tk.Label(root, text="Number of Users for Gas Computation")
# num_users_label.pack(pady=15)
# num_users_entry = tk.Entry(root)
# num_users_entry.pack(pady=5)
# compute_gas_button = tk.Button(root, text="Compute Gas", command=compute_gas)
# compute_gas_button.pack(pady=15)
#
# # Run the main Tkinter loop
# root.mainloop()
#
