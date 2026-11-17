def load_pier_data(start_year, end_year):
    """
    Load Scripps Pier data for a specified range of years.

    Parameters:
        start_year: First year to load (inclusive).
        end_year: Last year to load (inclusive).

    Returns:
        all_dnum: Array of timestamps (datetime64[s]).
        all_temperature: Array of temperatures (degrees C).
        all_pressure: Array of pressures (dbar).

        Outputs are returned in the order:
        time, temperature, pressure.
        
    """

    # Create empty lists to store each year's data
    all_time = []
    all_temperature = []
    all_pressure = [ ]

    # Loop through each year desired and load its corresponding NetCDF file
    for year in range(start_year, end_year + 1):
        filename = f'scripps_pier-{year}.nc'
        pier_file = os.path.join('..', '..', 'data', filename)

        nc = Dataset(pier_file)

        # Extract time and temperature arrays
        time_year = np.asarray(nc.variables['time'][:])
        temperature_year = np.asarray(nc.variables['temperature'][:])
        pressure_year = np.asarray(nc.variables['pressure'][:])

        nc.close()

        # Add each year's arrays to our lists
        all_time.append(time_year)
        all_temperature.append(temperature_year)
        all_pressure.append(pressure_year)

    # Combine individual yearly arrays into continuous arrays
    all_time = np.concatenate(all_time)
    all_temperature = np.concatenate(all_temperature)
    all_pressure = np.concatenate(all_pressure)

    # Convert timestamps into datetime format
    all_dnum = all_time.astype('datetime64[s]')

    #Make sure everything works
    #all_time and all_temperature must be identical
    print(len(all_time))
    print(len(all_temperature))
    print(len(all_pressure))

    #The dates should go from start to end date desired
    print(all_dnum[0])
    print(all_dnum[-1])

    # Return the combined temperature and datetime arrays
    return all_dnum, all_temperature, all_pressure