# Routing-Aware Features

This experiment uses the validated 16-node Blackhole and Sinkhole campaigns: five seeds, 240-second attack activation and 540-second runs.

RPL logging was set to `LOG_LEVEL_INFO` so generic DIO rank, parent switch, DIS and DAO information could be extracted. Attack markers were kept only to validate runs and were excluded from IDS features.

The folder also includes a seed-separated online-monitoring test. CUSUM is calibrated on Blackhole rank-state windows and applied to Sinkhole windows in time order. It uses generic low-rank routing-state features; labels and markers are used only when assessing the result.
