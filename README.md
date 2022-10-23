# DNV-hackathon
⛵💥🛥️

Method of reducing false positive collision candidates detection of ferrys in norway for risk analysis of the marine traffic in norway (AISyRISK), using Azure anomaly detection.

https://github.com/MicrosoftLearning/AI-900-AIFundamentals

General Workflow:
- Format AIS or AISyRISK candidates data from Veracity for anomaly detection
- Train Azure Anomaly detection algorythm on ferry data and export data 
- Compile all data in dataframe for final export and plotting



Spesific Script Workflow:

anomaly_detection/ - description coming soon™ 

Plotting files:

- /candidate_analysis/candidates_analisys.py - is used to load in AISyRisk candidates to quickly filter out desired ferries, dates, and candidate properties and get simple plots and statistics.

All plotting files in plotting/ are used for combining data from anonaly detection and AISyRISK candidates data and plot them. File names should be descriptive, but slight further insight for each is given here:

- check_ground_collision.py - use just AIS or candidates data, check for collisions and plot animated.
- check_ground_when_anomaly.py - use AIS or candidates data, include anomaly detection data and plot animated.
- check_ground_when_anomaly_resampled.py - use AIS or candidates data resampled for different polling rate, then check for collisions, remove points using anomaly detection and plot animated.
- check_ground_when_collision_and_anomaly.py - use candidate and anomaly detection data, then plot when there are both collision and anomaly overlap
- check_ground_when_collision_no_anomaly.py - use candidate and anomaly detection data, then plot when collisions dont overlap with anomalies
- check_with_turning.py
- plot_ferry_route_static.py - static (non animated) ferry plots for general use.
