FWR_SERVER_SERVICE = """[Unit]
After=network.target

[Service]
Type=notify
ExecStart=/usr/local/bin/fwr-server
Restart=always
RestartSec=10


[Install]
RequiredBy=network.target
"""
FWR_SYNC_SERVICE = """[Unit]
After=network.target

[Service]
Type=notify
ExecStart=/usr/local/bin/fwr-sync
Restart=on-failure
RestartSec=10


[Install]
RequiredBy=network.target
"""