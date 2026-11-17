function pier = sl_GetPierRecord(folder)
    %function pier =sl_GetPierRecord(folder)
    %Load multiyear SIO pier record from yearly nc files 
    %pier is the structure with the following fields: dnum, pressure, and temperature
    %Summer Lenhart 
    files = dir(fullfile(folder, '*.nc'));
    time_full=[];
    temp_full=[];
    flag_full=[];
    pressure_full=[];
    for j = 1:length(files)
    fname = fullfile(folder, files(j).name);
    tp = ncread(fname, 'temperature');
    t = ncread(fname, 'time');
    p=ncread(fname, 'pressure');
    time_full = [time_full; t];
    temp_full = [temp_full; tp];
    pressure_full = [pressure_full;p];
    end
    date0 = datenum(1970,1,1);
    dnum_full = double(time_full)/3600/24 +date0;
    pier.dnum=dnum_full;
    pier.temperature = temp_full;
    pier.pressure = pressure_full;
    pier.readme = 'Scripps Pier multi-year record, sl_GetPierRecord';
end
