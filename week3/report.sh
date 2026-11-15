
#!/usr/bin/env bash

set -euo pipefail

# Location where the HTML report will be published
OUTPUT_FILE="/var/www/html/viikko3/index.html"

# Function that determines the disk space status
get_disk_status() {
    local usage="$1"

    if (( usage < 80 )); then
        printf "OK"
    else
        printf "WARNING"
    fi
}

# Optional test mode for checking the disk status logic
if [[ "${1:-}" == "--test-status" ]]; then
    if [[ $# -ne 2 || ! "$2" =~ ^[0-9]+$ ]] || (( $2 > 100 )); then
        echo "Usage: $0 --test-status PERCENTAGE" >&2
        exit 1
    fi

    get_disk_status "$2"
    printf "\n"
    exit 0
fi

# Collect system information
generated_at=$(date '+%Y-%m-%d %H:%M:%S %Z (%z)')
uptime_info=$(uptime -p)

# Extract the root filesystem's usage percentage
disk_usage=$(df -P / | awk 'NR==2 {gsub(/%/, "", $5); print $5}')

# Extract total and available memory
ram_total=$(free -h | awk '/^Mem:/ {print $2}')
ram_available=$(free -h | awk '/^Mem:/ {print $7}')

# Determine disk space status
disk_status=$(get_disk_status "$disk_usage")

# Select a CSS class for the status indicator
if [[ "$disk_status" == "OK" ]]; then
    status_class="ok"
else
    status_class="warning"
fi

# Generate the HTML report
cat > "$OUTPUT_FILE" <<EOF
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Week 3 - Server Status</title>

    <style>
        body {
            font-family: Arial, sans-serif;
            background: #151521;
            color: #eeeeee;
            margin: 0;
            padding: 40px 20px;
        }

        main {
            max-width: 750px;
            margin: auto;
        }

        h1, h2 {
            color: #b69cff;
        }

        section {
            background: #232334;
            padding: 20px;
            margin: 20px 0;
            border-radius: 10px;
        }

        .status {
            font-weight: bold;
        }

        .ok {
            color: #65df9b;
        }

        .warning {
            color: #ffbd69;
        }

        .info {
            line-height: 1.8;
        }

        footer {
            color: #aaaaaa;
            margin-top: 30px;
            font-size: 0.9em;
        }
    </style>
</head>

<body>
<main>
    <h1>Week 3 - Server Status Report</h1>

    <section>
        <h2>System Information</h2>

        <div class="info">
            <p><strong>Report generated:</strong> $generated_at</p>
            <p><strong>Server uptime:</strong> $uptime_info</p>
            <p><strong>Root filesystem disk usage:</strong> $disk_usage%</p>
            <p><strong>Total RAM:</strong> $ram_total</p>
            <p><strong>Available RAM:</strong> $ram_available</p>
            <p>
                <strong>Disk space status:</strong>
                <span class="status $status_class">$disk_status</span>
            </p>
        </div>
    </section>

    <footer>
        <p>Linux Administration - Week 3 Assignment</p>
        <p>Automatically generated using Bash and Linux commands.</p>
	<p><a href="/viikko3/documentation.html">Assignment documentation</a></p>
	<p><a href="https://github.com/Paralax10/Linux-Administration">GitHub repository</a></p>
    </footer>
</main>
</body>
</html>
EOF

echo "Report successfully generated at $OUTPUT_FILE"
