from brownie import EnergyProfile, EnergyMarket, EnergyPool, network

def main():
    # Make sure to connect to the desired network
    # network.connect('development')  # Replace with the desired network

    # Get the latest deployed instances of the contracts
    energy_profile = EnergyProfile[-1]
    energy_market = EnergyMarket[-1]
    energy_pool = EnergyPool[-1]

    # Print the deployed contract addresses
    print("EnergyProfile deployed at:", energy_profile.address)
    print("EnergyMarket deployed at:", energy_market.address)
    print("EnergyPool deployed at:", energy_pool.address)

    # Disconnect from the network
    network.disconnect()
