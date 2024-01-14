# mahm-exporter

This Python 3 script converts MSI Afterburner Remote Server XML output into Prometheus metric format and serves on port 9183.

Sample output;
```
$ curl -s http://localhost:9183/metrics | head -3
# HELP mahm_gpu_temperature GPU temperature
# TYPE mahm_gpu_temperature gauge
mahm_gpu_temperature{srcUnits="C",localizedSrcName="GPU temperature",localizedSrcUnits="C",recommendedFormat="%.0f",minLimit="0",maxLimit="100",flags="SHOW_IN_OSD",gpu="0",srcId="0"} 53
```

MSI Afterburner Remote Server provides monitoring data in XML format.

An old version can be found here: https://download.cnet.com/msi-afterburner-remote-server/3000-20432_4-75871627.html

The default configuration is in "MSIAfterburnerRemoteServer.exe.config" file with these details;
```
address: http://localhost:82/mahm
username: MSIAfterburner
password: 17cc95b4017d496f82
```

Sample XML output;
```
$ curl -s -u "MSIAfterburner:17cc95b4017d496f82" http://localhost:82/mahm
<?xml version="1.0" encoding="utf-8"?>
<HardwareMonitor>
	<HardwareMonitorHeader>
		<signature>1296123981</signature>
		<version>131072</version>
		<headerSize>32</headerSize>
		<entryCount>25</entryCount>
		<entrySize>1324</entrySize>
		<time>1705094555</time>
		<gpuEntryCount>1</gpuEntryCount>
		<gpuEntrySize>1304</gpuEntrySize>
	</HardwareMonitorHeader>
	<HardwareMonitorEntries>
		<HardwareMonitorEntry>
			<srcName>GPU temperature</srcName>
			<srcUnits>C</srcUnits>
			<localizedSrcName>GPU temperature</localizedSrcName>
			<localizedSrcUnits>C</localizedSrcUnits>
			<recommendedFormat>%.0f</recommendedFormat>
			<data>44</data>
			<minLimit>0</minLimit>
			<maxLimit>100</maxLimit>
			<flags>SHOW_IN_OSD</flags>
			<gpu>0</gpu>
			<srcId>0</srcId>
		</HardwareMonitorEntry>
...
```

The tags in XML tree are converted into Prometheus labels.

mahm_exporter.py file connects to /mahm (probably acronym for MSI Afterburner Hardware Monitor?) on port 82 and reads XML everytime GET /metrics is requested.
